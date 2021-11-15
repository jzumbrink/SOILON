from django.shortcuts import render, redirect, get_object_or_404, Http404, HttpResponse
from .models import Kunde, Bodenprobe, Auftrag, PpmValue, Address
from .forms import *
from SoilonWorkflowSolutions import settings as project_settings
from .pdf_handling import handle_bodenprobe_auswertung
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse
from .backend_calculations import *
from .config import *
from .answer_pdf import create_answer_pdf
from math import ceil
import os
import math

from .templates_office.template3.root import create_doc


def index(request):
    if not request.user.is_authenticated:
        return redirect('admin:login')
    return redirect('main')


@login_required
def welcome_screen(request):
    return_dict = getKundenListe(request)
    return_dict['user'] = request.user
    return_dict['url'] = 'main'
    return render(request, 'workflow/main.html', return_dict)


@login_required
def new_customer(request):
    if request.method == "POST":
        form = NewCustomer(request.POST)
        if form.is_valid():
            try:
                geschlecht = form.cleaned_data['geschlecht'][0]
            except IndexError:
                geschlecht = ''
            k = Kunde.objects.create(
                nachname=form.cleaned_data['nachname'],
                vorname=form.cleaned_data['vorname'],
                plz=form.cleaned_data['plz'],
                wohnort=form.cleaned_data['wohnort'],
                strasse=form.cleaned_data['strasse'],
                hausnummer=form.cleaned_data['hausnummer'],
                land=form.cleaned_data['land'],
                adresszusatz=form.cleaned_data['adresszusatz'],
                telefonnummer=form.cleaned_data['telefonnummer'],
                email=form.cleaned_data['email'],
                registrierungs_zeit=timezone.now(),
                geschlecht=geschlecht,
                titel=form.cleaned_data['titel'],
            )
            print(reverse(add_customer_successful))
            url = reverse(add_customer_successful) + "?kunden_id={}".format(str(k.id))
            return HttpResponseRedirect(reverse(kunde_details_success_msg, kwargs={'kunde_id': k.id, 'success': 1}))
    form = NewCustomer()
    return render(request, 'workflow/neuen_kunde_anlegen.html', {
        'form': form,
    })


def getKundenListe(request):
    # Customer Pages fangen mit 1 an. Einfach weil es deshalb einfacher ist 'zureck_url' für die erste Seite anzugeben
    kunden_liste = Kunde.objects.all().order_by('-registrierungs_zeit')
    anzahl_kunden = len(kunden_liste)
    if 'page_customers' in request.GET.keys():
        # Es wird angegeben, welche Kunden angezeigt werden sollen
        page_customers = int(request.GET.get('page_customers')) - 1
        kunden_liste = kunden_liste[page_customers * customers_per_site:min(anzahl_kunden,
                                                                            page_customers * customers_per_site + customers_per_site)]
    else:
        kunden_liste = kunden_liste[0:customers_per_site]
        page_customers = 0
    return_dict = {'kunden': kunden_liste,
                   'aktuelle_seite': page_customers + 1,
                   'seiten_ges': ceil(anzahl_kunden / customers_per_site),
                   }
    if page_customers > 0:  # Es kann eine Seite zurück gegangen werden
        # return_dict['zurueck_url'] = reverse('main')[:] + '?page_customers=' + str(page_customers - 1)
        return_dict['zurueck_url'] = page_customers
    else:
        print(page_customers, "ppp")
    if page_customers < return_dict['seiten_ges'] - 1:  # Es gibt eine nächste Seite
        # return_dict['weiter_url'] = reverse('main')[:] + '?page_customers=' + str(page_customers + 1)
        return_dict['weiter_url'] = page_customers + 2
    return return_dict


@login_required
def http_error(request, error_title=None, error_details="Es ist ein Fehler aufgetreten"):
    if error_title is not None:
        # Fehlermeldung mit Titel und Content
        return HttpResponseRedirect(
            reverse(raise_error) + "?error_title={}&error_details={}".format(error_title, error_details))
    else:
        # Fehlermeldung mit Content
        return HttpResponseRedirect(reverse(raise_error) + "?error_details={}".format(error_details))


@login_required
def returnPdfUpload1(request):
    # Erster Schritt, das Formular übermitteln
    form = ChooseOrder()
    auftrags_liste = [auftrag for auftrag in Auftrag.objects.all().order_by('-eingangs_zeit')]
    namen_kunden_liste = ["{0} {1} ({2})".format(Kunde.objects.filter(pk=kunden_id)[0].vorname,
                                                 Kunde.objects.filter(pk=kunden_id)[0].nachname,
                                                 kunden_id) for kunden_id in [a.kunden_id for a in auftrags_liste]]
    return_obj = (auftrags_liste, namen_kunden_liste,)
    return render(request, 'workflow/upload_pdf_1.html',
                  {'form': form,
                   'auftraege_liste': [[return_obj[0][i],
                                        return_obj[1][i],
                                        getPercentageAuftragBodenproben(return_obj[0][i].id, [4, 5])
                                        ] for i in range(len(auftrags_liste))],
                   }
                  )


@login_required
def upload_soil_sample_result(request):
    # falls mit GET angegeben wird, um welcher Schritt es sich handelt
    if 'step' in request.GET.keys():
        if request.GET.get('step') == '0':
            return returnPdfUpload1(request)
        elif request.GET.get('step') == '1':
            form = ChooseOrder(request.POST)
            if form.is_valid():
                # prüfen, ob die Auftrags ID korrekt ist
                if Auftrag.objects.filter(pk=form.cleaned_data['auftrags_id']).count() == 0:
                    return http_error(request, error_details="Die Auftrags ID: {} ist nicht im System vorhanden".format(
                        form.cleaned_data['auftrags_id']))
                # Liste mit allen Bodenproben, über die der Auftrag verfügt
                bodenprobe_ids = [bodenprobe.id for bodenprobe in
                                  Bodenprobe.objects.filter(auftrags_id=form.cleaned_data['auftrags_id'])]
                if len(bodenprobe_ids) == 0:
                    return http_error(request,
                                      "IndexError",
                                      "Für die Auftragsnummer {} sind keine Bodenproben zugewiesen!".format(
                                          form.cleaned_data['auftrags_id']))
                auftrag = Auftrag.objects.filter(pk=form.cleaned_data['auftrags_id'])[0]
                kunden_daten = Kunde.objects.filter(pk=auftrag.kunden_id)[0]
                bodenprobe_upload_form = UploadPdfBodenprobeFile(auftrag_id=form.cleaned_data['auftrags_id'])
                # Die Auswhlmöglichkeiten für die Bodenprobe machen
                # bodenprobe_upload_form.bodenprobe_id.choices = [
                #   (bodenprobe_id, "{0}: {1}".format(bodenprobe_id, Bodenprobe.objects.get(pk=bodenprobe_id).label_name)) for bodenprobe_id in bodenprobe_ids
                # ]
                return render(request, 'workflow/upload_pdf_2.html', {
                    'auftrag': auftrag,
                    'bodenproben_list': bodenprobe_ids[:-1],
                    'letzte_bodenprobe_id': bodenprobe_ids[-1],
                    'kunden_daten': kunden_daten,
                    'form': UploadPdfBodenprobeFile(auftrag_id=auftrag.id),
                })
        elif request.GET.get('step') == '2':
            print(request.POST['bodenprobe_id'])
            probe_id = request.POST['bodenprobe_id']
            auftrags_id = Bodenprobe.objects.get(pk=probe_id).auftrags_id
            form = UploadPdfBodenprobeFile(auftrags_id, request.POST, request.FILES)
            # checks if form is valid
            if form.is_valid():
                if form.cleaned_data['pdf_bodenprobe_file'].name.split('.')[-1] != 'pdf':
                    return pdf_failed(request,
                                      "WrongFiletype: {0} ist kein gültiges Pdf-Dokument. Bitte benutze die \".pdf\"-Endung".format(
                                          form.cleaned_data['pdf_bodenprobe_file'].name))

                b = form.cleaned_data['bodenprobe_id']
                # Das originale pdf in media speichern
                # b.pdf_original = form.cleaned_data['pdf_bodenprobe_file']
                # b.save()

                # Den Auftrag bestimmen
                a = Auftrag.objects.get(pk=b.auftrags_id)

                # die Kunden id ermittel u.a. für den Antworttext
                kunden_id = Kunde.objects.get(pk=a.kunden_id).id

                generated_txt = handle_bodenprobe_auswertung(form.cleaned_data['pdf_bodenprobe_file'],
                                                             kunden_id,
                                                             b.auftrags_id,
                                                             b.id,
                                                             )
                Bodenprobe.objects.filter(pk=b.pk).update(mail_text=generated_txt[0],
                                                          raw_data_path=generated_txt[1],
                                                          raw_filename=generated_txt[2],
                                                          status=4,
                                                          results_upload_time=timezone.now(),
                                                          )
                # Zu der Bodenprobe leiten
                return HttpResponseRedirect(reverse(bodenprobe_details, kwargs={
                    'bodenprobe_id': b.id}) + "?msg=Die Daten wurden erfolgreich hochgeladen!")
            else:
                return HttpResponseRedirect(reverse(raise_error) + "?error_details=Das Formular ist nicht gültig")

        return HttpResponseRedirect(reverse(
            raise_error) + "?error_details=step darf nur die Werte 0, 1 und 2 annehmen. Jeder andere Wert ist beim Hochladen eines Pdf-Formulars unzulässig")
    elif request.method == 'POST':
        pass

    return returnPdfUpload1(request)


@login_required
def pdf_succeed(request, m_id):
    kunden_text = Bodenprobe.objects.filter(pk=m_id).values('mail_text')
    print(kunden_text)
    return render(request, 'workflow/pdf_succeed.html', {'kunden_text': kunden_text[0]['mail_text']})


@login_required
def order_overview(request):
    """bodenproben = Bodenprobe.objects.order_by('id').values('id', 'kunden_id', 'raw_filename')
    for i in range(len(bodenproben)):
        kunden_daten = Kunde.objects.filter(pk=bodenproben[i]['kunden_id']).values('nachname', 'vorname')
        print(kunden_daten)
        try:
            bodenproben[i]['kunden_id'] = "{0}, {1}".format(kunden_daten[0]['nachname'], kunden_daten[0]['vorname'])
        except IndexError:
            bodenproben[i]['kunden_id'] = "Undef kunden_id"
    print(bodenproben)"""
    auftraege = []
    for auftrag in Auftrag.objects.all().order_by('-eingangs_zeit'):
        try:
            kunde = Kunde.objects.filter(id=auftrag.kunden_id)[0]
        except IndexError:  # Kunde wurde gelöscht
            continue
        a = {
            'id': auftrag.id,
            'label_name': auftrag.label_name,
            'vorname': kunde.vorname,
            'nachname': kunde.nachname,
            'count_bodenproben': Bodenprobe.objects.filter(auftrags_id=auftrag.id).count(),
            'prg_probe_vorliegend': getPercentageAuftragBodenproben(auftrag.id, [1, 2, 3, 4, 5]),
            'prg_probe_getrocknet': getPercentageAuftragBodenproben(auftrag.id, [2, 3, 4, 5]),
            'prg_ergebnisse_weiter': auftrag.ergebnisse_zurueckgemeldet,
            'prg_probe_analysiert': getPercentageAuftragBodenproben(auftrag.id, [4, 5]),
            'prg_kundendaten': getPercentageKundendaten(auftrag.kunden_id),
        }
        if auftrag.bereits_gezahlt:
            a['bool_bezahlt'] = True
        auftraege.append(a)
    return render(request, 'workflow/auftrags_uebersicht.html', {
        'auftraege': auftraege
    })


@login_required
def pdf_failed(request, error):
    return render(request, 'workflow/pdf_failed.html', {'error': error})


''''@login_required
def details_bodenprobeOld(request, messung_id):
    bodenprobe = get_object_or_404(Bodenprobe, pk=messung_id)
    return render(request, 'workflow/display-details-bodenprobe.html',
                  {'messung_id': messung_id,
                   'kunden_id': bodenprobe.kunden_id,
                   'data_path': bodenprobe.raw_data_path,
                   'filename': bodenprobe.raw_filename,
                   'text': bodenprobe.mail_text,
                   'info': bodenprobe.extra_info})
'''


@login_required
def workflow_guide(request):
    return render(request, 'workflow/informationen_workflow.html')


@login_required
def new_order(request):
    if request.method == 'POST':
        form = NewOrder(request.POST)
        if form.is_valid():
            if Kunde.objects.filter(pk=form.cleaned_data['kunden_id']).count() <= 0:
                return HttpResponseRedirect(reverse(raise_error) + "?error_content={}".format("Ungültige Kunden ID"))
            o = Auftrag.objects.create(
                kunden_id=form.cleaned_data['kunden_id'],
                anzahl_bodenproben=form.cleaned_data['anzahl_bodenproben'],
                preis=form.cleaned_data['preis'],
                bereits_gezahlt=form.cleaned_data['payment_received'],
                label_name=form.cleaned_data['custom_name'],
                notizen=form.cleaned_data['extra_info'],
                eingangs_zeit=timezone.now(),
            )
            # Neue Bodenproben erstellen
            for i in range(o.anzahl_bodenproben):
                Bodenprobe.objects.create(
                    auftrags_id=o.id,
                    status=0,
                    results_upload_time=timezone.now(),
                )
            return HttpResponseRedirect(
                reverse(auftrag_details_success_msg, kwargs={'auftrags_id': o.id, 'success': 1}))
        else:
            return HttpResponseRedirect(
                reverse(raise_error) + "?error_title={}&error_content={}".format("Formular ist nicht gültig",
                                                                                 "Das Formular ist ungültig"))

    form = NewOrder()
    return_dict = getKundenListe(request)
    return_dict['form'] = form
    return_dict['url'] = 'new_order'
    return render(request, 'workflow/new_order.html', return_dict)


@login_required
def search_database(request):
    provided_data = {}
    alle_objekte = None

    # Zuerst einmal je nach Wert die Objekte der Klasse abfragen
    if "choosen_class" in request.GET.keys():
        db_class = request.GET.get("choosen_class").lower()
        if db_class == "kun":
            # Kunden
            provided_data["kun_selected"] = 1
            alle_objekte = Kunde.objects.all()
        elif db_class == "auf":
            # Aufträge
            provided_data["auf_selected"] = 1
            alle_objekte = Auftrag.objects.all()
        elif db_class == "bod":
            # Bodenproben
            provided_data["bod_selected"] = 1
            alle_objekte = Bodenprobe.objects.all()
        else:
            return HttpResponseRedirect(reverse(raise_error) + "?error_details={}".format(
                "Die Bezeichnung \"" + db_class + "\" ist ungültig und konnte keiner Suchfunktion zugeordnet werden!"))

    if "search" in request.GET.keys() and len(request.GET.get("search")) != 0:
        search_string = request.GET.get("search")
        objekt_score_liste = []
        for objekt in alle_objekte:
            score = getComparisionScore(search_string, objekt, suchkriterien[db_class])
            objekt_score_liste.append({'score': score, 'obj': objekt})

        obj_daten = [{'data': [obj['obj'].__dict__[kriterium] for kriterium in suchergebniss_spalten[db_class]],
                      'score': obj['score'], 'id': obj['obj'].id} for obj in
                     (sorted(objekt_score_liste, key=lambda l: l['score'], reverse=True)) if obj['score'] > 0.55]

        provided_data['baselink'] = baselink[db_class]
        provided_data['suchword'] = search_string
        provided_data['suchergebniss_spalten'] = suchergebniss_spalten[db_class]
        provided_data['anzahl_ergebnisse'] = len(obj_daten) if len(obj_daten) > 0 else -1

        # Die Zahl der Ergebnisse pro Seite bestimmen
        if "results_per_page" in request.GET.keys():
            results_per_page = int(request.GET.get("results_per_page"))
        else:
            results_per_page = 10

        provided_data["init_results_per_page"] = results_per_page
        provided_data['count_pages'] = int(math.ceil(len(obj_daten) / results_per_page))

        # Berechnen, welche der Ergebnisse angezeigt werden
        if "page" in request.GET.keys():
            try:
                page = int(request.GET.get("page"))
            except ValueError:
                page = 1
            page = min(page, provided_data['count_pages'])
            provided_data['init_page'] = page
            min_index = (page - 1) * results_per_page
            max_index = page * results_per_page - 1
            if len(obj_daten) > max_index + 1:
                provided_data['obj_daten'] = obj_daten[min_index:max_index + 1]
            else:
                provided_data['obj_daten'] = obj_daten[min_index:]
        else:
            provided_data['init_page'] = 1
            if len(obj_daten) > 10:
                provided_data['obj_daten'] = obj_daten[:10]
            else:
                provided_data['obj_daten'] = obj_daten

        return render(request, 'workflow/browse_database.html', provided_data)
    else:
        provided_data['anzahl_ergebnisse'] = -2
        return render(request, 'workflow/browse_database.html', provided_data)


@login_required
def add_customer_successful(request):
    try:
        kunden_daten = Kunde.objects.filter(pk=request.GET.get('kunden_id'))[0]
        return render(request, 'workflow/kunde_anlegen_erfolgreich.html', {
            'kunden_daten': kunden_daten
        })
    except IndexError:
        return HttpResponseRedirect(
            reverse(raise_error) + "?error_details={}".format("Die Kunden ID wurde nicht mittels \"GET\" übermittelt"))


@login_required
def raise_error(request):
    if request.method == "GET":
        try:
            error_content = request.GET.get('error_details')
            try:
                error_title = request.GET.get('error_title')
                return render(request, 'workflow/error.html', {
                    'error_title': error_title,
                    'error_content': error_content
                })
            except IndexError:
                return render(request, 'workflow/error.html', {
                    'error_content': error_content
                })
        except IndexError:
            return render(request, 'workflow/error.html', {
                'error_content': "Die Details des Fehlers sind bei der Weiterleitung zur Fehler-Anzeige verloren gegangen"
            })
    else:
        return render(request, 'workflow/error.html', {
            'error_content': "Die Details des Fehlers sind bei der Weiterleitung zur Fehler-Anzeige verloren gegangen"
        })


def getPpmValue(element, bodenprobe_id):
    try:
        return PpmValue.objects.filter(
            bodenprobe_id=bodenprobe_id,
            element=element
        )[0].value
    except IndexError:
        # Keine Daten vorhanden bisher
        return '/'


def createAuftragDict(auftrags_id):
    auftrag = get_object_or_404(Auftrag, pk=auftrags_id)
    kunde = get_object_or_404(Kunde, pk=auftrag.kunden_id)
    # Hinzu kommt eine Tabelle mit allen Bodenproben
    bodenprobe_list = [{
        'id': bodenprobe.id,
        'label_name': bodenprobe.label_name,
        'extra_info': bodenprobe.extra_info,
        'cd': getPpmValue('cd', bodenprobe.id),
        'pb': getPpmValue('pb', bodenprobe.id),
        'cu': getPpmValue('cu', bodenprobe.id),
        'zn': getPpmValue('zn', bodenprobe.id),
        'cr': getPpmValue('cr', bodenprobe.id),
        'ni': getPpmValue('ni', bodenprobe.id),
        'as': getPpmValue('as', bodenprobe.id),
    } for bodenprobe in Bodenprobe.objects.filter(auftrags_id=auftrags_id)]
    form = UpdateAuftrag()
    return {'auftrags_id': auftrags_id,
            'auftrag': auftrag,
            'kunde': kunde,
            'bodenproben': bodenprobe_list,
            'form': form,
            }


@login_required
def order_details(request, order_id):
    if request.method == 'POST':
        form = UpdateAuftrag(request.POST)
        if form.is_valid():
            print(form)
            print(form.cleaned_data['bereits_gezahlt'])
            Auftrag.objects.filter(pk=order_id).update(bereits_gezahlt=form.cleaned_data['bereits_gezahlt'])
            return HttpResponseRedirect(
                reverse(auftrag_details_success_msg, kwargs={'auftrags_id': order_id, 'success': 2}))
    return render(request, 'workflow/auftrag_details.html', createAuftragDict(order_id))


@login_required
def auftrag_details_success_msg(request, auftrags_id, success):
    """
    Success IDS:
    1: Object successfully created
    2: Payment Status successfully changed
    """
    if request.method == 'POST':
        return order_details(request, auftrags_id)
    auftrag_dict = createAuftragDict(auftrags_id)
    if success == 1:
        auftrag_dict['msg_head'] = "Der Auftrag konnte erfolgreich erstellt werden!"
    elif success == 2:
        auftrag_dict['msg_head'] = "Der Status der Bezahlung wurde erfolgreich geändert!"
    return render(request, 'workflow/auftrag_details.html', auftrag_dict)


def createKundeDict(kunde_id):
    kunde = get_object_or_404(Kunde, pk=kunde_id)
    auftraege = Auftrag.objects.filter(kunden_id=kunde_id)
    return {'kunde_id': kunde_id,
            'kunde': kunde,
            'auftraege_liste': auftraege,
            'anzahl_auftraege': len(auftraege),
            }


@login_required
def kunde_details(request, kunde_id):
    return render(request, 'workflow/kunde_details.html', createKundeDict(kunde_id))


def kunde_details_success_msg(request, kunde_id, success):
    kunde_dict = createKundeDict(kunde_id)
    kunde_dict['erfolgreich_erstellt'] = True
    return render(request, 'workflow/kunde_details.html', kunde_dict)


@login_required
def bodenprobe_details(request, bodenprobe_id):
    bodenprobe = get_object_or_404(Bodenprobe, pk=bodenprobe_id)

    if request.method == 'POST':
        form = UpdateSoilSample(request.POST)
        if form.is_valid():
            # TODO update/create alternate address
            Bodenprobe.objects.filter(pk=bodenprobe_id).update(is_billing_address_sampling_point=form.cleaned_data['is_billing_address_sampling_point'])
            Bodenprobe.objects.filter(pk=bodenprobe_id).update(status=form.cleaned_data['status_id'])
        return HttpResponseRedirect(reverse(bodenprobe_details, kwargs={'bodenprobe_id': bodenprobe_id}))

    try:
        auftrag = Auftrag.objects.filter(pk=bodenprobe.auftrags_id)[0]
    except IndexError:
        auftrag = None

    if auftrag is not None:
        try:
            kunde = Kunde.objects.filter(pk=auftrag.kunden_id)[0]
        except IndexError:
            kunde = None
    else:
        kunde = None

    msg = None
    if 'msg' in request.GET.keys():
        msg = request.GET.get('msg')

    bodenprobe_list = [{
        'id': bodenprobe.id,
        'label_name': bodenprobe.label_name,
        'extra_info': bodenprobe.extra_info,
        'cd': getPpmValue('cd', bodenprobe.id),
        'pb': getPpmValue('pb', bodenprobe.id),
        'cu': getPpmValue('cu', bodenprobe.id),
        'zn': getPpmValue('zn', bodenprobe.id),
        'cr': getPpmValue('cr', bodenprobe.id),
        'ni': getPpmValue('ni', bodenprobe.id),
        'as': getPpmValue('as', bodenprobe.id),
    }, ]

    answer_filename = 'Auswertung-{0}-{1}-{2}.{3}'.format(kunde.vorname, kunde.nachname, bodenprobe.id,
                                                          'pdf' if microsoft_word_installed else 'docx')
    initial_form_dict = {
                          'status_id': bodenprobe.status,
                          'is_billing_address_sampling_point': bodenprobe.is_billing_address_sampling_point,
                      }

    if bodenprobe.alt_sampling_point_address_id >= 0:
        alt_address = get_object_or_404(Address, pk=bodenprobe.alt_sampling_point_address_id)
        initial_form_dict['alt_zip_code'] = alt_address.zip_code
        initial_form_dict['alt_city'] = alt_address.alt_city
        initial_form_dict['alt_street'] = alt_address.alt_street
        initial_form_dict['alt_house_number'] = alt_address.alt_house_number
        initial_form_dict['alt_country'] = alt_address.alt_country
        initial_form_dict['alt_address_suffix'] = alt_address.alt_address_suffix

    return render(request, 'workflow/bodenprobe_details.html',
                  {
                      'bodenproben': bodenprobe_list,
                      'auftrag': auftrag,
                      'kunde': kunde,
                      'msg': msg,
                      'answer_filename': answer_filename,
                      'status': bodenprobe.status,
                      'form': UpdateSoilSample(initial=initial_form_dict),
                  }
                  )


@login_required
def generate_pdf_answer_customer_file(request, bodenprobe_id, filename):
    create_answer_pdf(bodenprobe_id, filename)


def get_soil_sample_id_from_filename(filename):
    name = filename.split('.')[0]
    return int(name.split('-')[-1])


@login_required
def download_file(request, inner_folder, filename):
    path = os.path.join(project_settings.MEDIA_ROOT, inner_folder, filename)
    print(inner_folder)
    print(filename)
    print(path)
    if inner_folder == 'ana_answer' and Bodenprobe.objects.filter(
            pk=get_soil_sample_id_from_filename(filename)).count() == 1:
        # Pdf als Antwort für den Kunden generieren
        generate_pdf_answer_customer_file(request, get_soil_sample_id_from_filename(filename), filename)
    if os.path.exists(path):
        # Ein Pdf-Dokument als Antwort für den Kunden soll heruntergeladen werden
        with open(path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/force-download')
            return response
    raise Http404


@login_required
def analytics(request):
    return render(request, 'workflow/analytics.html')