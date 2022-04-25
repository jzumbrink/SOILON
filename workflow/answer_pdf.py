import os
from datetime import date
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from .models import Kunde, Auftrag, Bodenprobe, PpmValue
from .database_operations import get_ppm_value
from .color_bars import createImg, create_dummy_img
from SoilonWorkflowSolutions import settings as project_settings
from .config import microsoft_word_installed, used_elements, template_filename, invoice_tpl_filename, soil_sample_price
from docx2pdf import convert

month_map: dict = {
    1: "Januar",
    2: "Februar",
    3: "März",
    4: "April",
    5: "Mai",
    6: "Juni",
    7: "Juli",
    8: "August",
    9: "September",
    10: "Oktober",
    11: "November",
    12: "Dezember",
}


def basic_customer_context(customer: Kunde) -> dict:
    return {
        'title': customer.titel + ' ' if len(customer.titel) > 0 else '',
        'first_name': customer.vorname,
        'surname': customer.nachname,
        'street': customer.strasse,
        'house_number': str(customer.hausnummer),
        'zip_code': str(customer.plz),
        'city': customer.wohnort,
        'address': "Sehr geehrte Frau" if customer.anrede == "Frau" or customer.geschlecht == 'w' else (
            "Sehr geehrter Herr" if customer.anrede == "Herr" or customer.geschlecht == 'm' else "Sehr geehrte/r Frau/Herr"),
    }


def basic_date_context() -> dict:
    today = date.today()
    return {
        'day': str(today.day),
        'month_de': month_map[today.month],
        'year': str(today.year),
    }


def create_answer_pdf(soil_sample_id: int, filename: str):
    filename = '.'.join(filename.split('.')[:-1])
    filename_docx = filename + '.docx'

    target_folder = os.path.join(project_settings.MEDIA_ROOT, 'ana_answer')
    target_file_docx = os.path.join(target_folder, filename_docx)
    img_temp_folder = os.path.join(target_folder, 'temp')

    tpl_filename = os.path.join(project_settings.STATIC_ROOT, 'tpl_office', template_filename)
    tpl = DocxTemplate(tpl_filename)

    soil_sample = Bodenprobe.objects.get(pk=soil_sample_id)
    order = Auftrag.objects.get(pk=soil_sample.auftrags_id)
    customer = Kunde.objects.get(pk=order.kunden_id)

    img_filenames = {}
    for element in used_elements:
        img_filenames[element] = os.path.join(img_temp_folder, 'img_{0}_{1}.png'.format(soil_sample_id, element))
        if PpmValue.objects.filter(element=element, bodenprobe_id=soil_sample_id).__len__() > 0:
            createImg(img_filenames[element], element, get_ppm_value(element, soil_sample_id))
        else:
            create_dummy_img(img_filenames[element])

    context: dict = {
        'heading': "Ihre Analyse",
        'cd_img': InlineImage(tpl=tpl, image_descriptor=img_filenames['cd'], width=Mm(162)),
        'cd_val': str(get_ppm_value('cd', soil_sample_id)) + " ppm",
        'cu_img': InlineImage(tpl=tpl, image_descriptor=img_filenames['cu'], width=Mm(162)),
        'cu_val': str(get_ppm_value('cu', soil_sample_id)) + " ppm",
        'pb_img': InlineImage(tpl=tpl, image_descriptor=img_filenames['pb'], width=Mm(162)),
        'pb_val': str(get_ppm_value('pb', soil_sample_id)) + " ppm",
        'zn_img': InlineImage(tpl=tpl, image_descriptor=img_filenames['zn'], width=Mm(162)),
        'zn_val': str(get_ppm_value('zn', soil_sample_id)) + " ppm",
        'ni_img': InlineImage(tpl=tpl, image_descriptor=img_filenames['ni'], width=Mm(162)),
        'ni_val': str(get_ppm_value('ni', soil_sample_id)) + " ppm",
        'as_img': InlineImage(tpl=tpl, image_descriptor=img_filenames['as'], width=Mm(162)),
        'as_val': str(get_ppm_value('as', soil_sample_id)) + " ppm",
    }
    context.update(basic_customer_context(customer))
    context.update(basic_date_context())

    tpl.render(context=context)

    tpl.save(target_file_docx)

    if microsoft_word_installed and False:  # TODO remove "and False" and test with existing Word installation
        target_file_pdf = os.path.join(target_folder, filename + '.pdf')
        convert(target_file_docx, target_file_pdf)

    # delete all generated images from disk
    for img_filename in img_filenames:
        if os.path.isfile(img_filename):
            os.remove(img_filename)


def invoice_contents_and_sum(order: Auftrag):
    invoice_contents = [{
        'position': 1,
        'count': order.anzahl_bodenproben,
        'description': "Schwermetallanalyse As, Cd, Cu, Ni, Pb und Zn mittels RFA",
        'single_price': "{0:,.2f}".format(soil_sample_price).replace('.', ','),
        'combined_price': "{0:,.2f}".format(soil_sample_price * order.anzahl_bodenproben).replace('.', ','),
    }]
    # TODO implement entries from other services
    combined_sum = "{0:,.2f}".format(soil_sample_price * order.anzahl_bodenproben).replace('.', ',')
    return combined_sum, invoice_contents


def create_invoice_pdf(order_id: int, filename: str):
    filename = '.'.join(filename.split('.')[:-1])
    filename_docx = filename + '.docx'

    target_folder = os.path.join(project_settings.MEDIA_ROOT, 'invoices')
    target_file_docx = os.path.join(target_folder, filename_docx)

    tpl_filename = os.path.join(project_settings.STATIC_ROOT, 'tpl_office', invoice_tpl_filename)
    tpl = DocxTemplate(tpl_filename)

    order = Auftrag.objects.get(pk=order_id)
    customer = Kunde.objects.get(pk=order.kunden_id)

    combined_sum, invoice_contents = invoice_contents_and_sum(order)
    context = {
        'invoice_contents': invoice_contents,
        'combined_sum': combined_sum,
        'order_id': str(order_id),
        'customer_id': str(customer.id),
        'first_name': customer.vorname,
        'payment_details': "Zahlungsbedingungen: Zahlung innerhalb von 7 Tagen ab Rechnungseingang ohne Abzüge." if not order.bereits_gezahlt else "Der Betrag wurde bereits überwiesen.",
    }
    context.update(basic_customer_context(customer))
    context.update(basic_date_context())

    tpl.render(context=context)
    tpl.save(target_file_docx)
