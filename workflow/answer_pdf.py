import os
from datetime import date
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from .models import Kunde, Auftrag, Bodenprobe, PpmValue
from .color_bars import createImg, create_dummy_img
from SoilonWorkflowSolutions import settings as project_settings
from .config import microsoft_word_installed, used_elements
from docx2pdf import convert

template_filename = 'tpl_5.docx'

month_map = {
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

# TODO duplicate -> merge into another file for better usage
def getPpmValue(element, bodenprobe_id):
    try:
        return PpmValue.objects.filter(
            bodenprobe_id=bodenprobe_id,
            element=element
        )[0].value
    except IndexError:
        # Keine Daten vorhanden bisher
        return '/'


def create_answer_pdf(soil_sample_id, filename):
    filename = '.'.join(filename.split('.')[:-1])
    filename_docx = filename + '.docx'
    print(os.path.abspath(__file__))
    print(os.getcwd())

    current_path = os.getcwd().replace(os.sep, '/')

    print(current_path)
    target_folder = os.path.join('', './media/ana_answer/')
    print(target_folder)
    target_folder = os.path.join(project_settings.MEDIA_ROOT, 'ana_answer')
    print(target_folder)
    target_file_docx = os.path.join(target_folder, filename_docx)
    print(target_file_docx)
    img_temp_folder = os.path.join(target_folder, 'temp')
    print(img_temp_folder)

    # img_filename_cd = os.path.join(img_temp_folder, 'img_{0}_{1}.png'.format(soil_sample_id, 'cd'))
    # img_filename_cu = os.path.join(img_temp_folder, 'img_{0}_{1}.png'.format(soil_sample_id, 'cu'))
    # img_filename_pb = os.path.join(img_temp_folder, 'img_{0}_{1}.png'.format(soil_sample_id, 'pb'))
    # img_filename_zn = os.path.join(img_temp_folder, 'img_{0}_{1}.png'.format(soil_sample_id, 'zn'))
    # img_filenames = [img_filename_cd, img_filename_cu, img_filename_pb, img_filename_zn]

    tpl_filename = os.path.join(project_settings.STATIC_ROOT, 'tpl_office', template_filename)
    tpl = DocxTemplate(tpl_filename)

    soil_sample = Bodenprobe.objects.get(pk=soil_sample_id)
    order = Auftrag.objects.get(pk=soil_sample.auftrags_id)
    customer = Kunde.objects.get(pk=order.kunden_id)

    today = date.today()

    # createImg(img_filename_cd, 'cd', getPpmValue('cd', soil_sample_id))
    # createImg(img_filename_cu, 'cu', getPpmValue('cu', soil_sample_id))
    # createImg(img_filename_pb, 'pb', getPpmValue('pb', soil_sample_id))
    # createImg(img_filename_zn, 'zn', getPpmValue('zn', soil_sample_id))
    img_filenames = {}
    for element in used_elements:
        img_filenames[element] = os.path.join(img_temp_folder, 'img_{0}_{1}.png'.format(soil_sample_id, element))
        if PpmValue.objects.filter(element=element, bodenprobe_id=soil_sample_id).__len__() > 0:
            createImg(img_filenames[element], element, getPpmValue(element, soil_sample_id))
        else:
            create_dummy_img(img_filenames[element])

    context = {
        'title': customer.titel + ' ' if len(customer.titel) > 0 else '',
        'first_name': customer.vorname,
        'surname': customer.nachname,
        'street': customer.strasse,
        'house_number': str(customer.hausnummer),
        'zip_code': str(customer.plz),
        'city': customer.wohnort,
        'day': str(today.day),
        'month_de': month_map[today.month],
        'year': str(today.year),
        'heading': "Ihre Analyse",
        'address': "Sehr geehrte Frau" if customer.anrede == "Frau" or customer.geschlecht == 'w' else ("Sehr geehrter Herr" if customer.anrede == "Herr" or customer.geschlecht == 'm' else "Sehr geehrte/r Frau/Herr"),
        'cd_img': InlineImage(tpl=tpl, image_descriptor=img_filenames['cd'], width=Mm(162)),
        'cd_val': str(getPpmValue('cd', soil_sample_id)) + " ppm",
        'cu_img': InlineImage(tpl=tpl, image_descriptor=img_filenames['cu'], width=Mm(162)),
        'cu_val': str(getPpmValue('cu', soil_sample_id)) + " ppm",
        'pb_img': InlineImage(tpl=tpl, image_descriptor=img_filenames['pb'], width=Mm(162)),
        'pb_val': str(getPpmValue('pb', soil_sample_id)) + " ppm",
        'zn_img': InlineImage(tpl=tpl, image_descriptor=img_filenames['zn'], width=Mm(162)),
        'zn_val': str(getPpmValue('zn', soil_sample_id)) + " ppm",
        'cr_img': InlineImage(tpl=tpl, image_descriptor=img_filenames['cr'], width=Mm(162)),
        'cr_val': str(getPpmValue('cr', soil_sample_id)) + " ppm",
        'ni_img': InlineImage(tpl=tpl, image_descriptor=img_filenames['ni'], width=Mm(162)),
        'ni_val': str(getPpmValue('ni', soil_sample_id)) + " ppm",
        'as_img': InlineImage(tpl=tpl, image_descriptor=img_filenames['as'], width=Mm(162)),
        'as_val': str(getPpmValue('as', soil_sample_id)) + " ppm",
    }

    tpl.render(context=context)

    tpl.save(target_file_docx)

    if microsoft_word_installed and False:  # TODO remove "and False" and test with existing Word installation
        target_file_pdf = os.path.join(target_folder, filename + '.pdf')
        convert(target_file_docx, target_file_pdf)

    # delete all generated images from disk
    for img_filename in img_filenames:
        if os.path.isfile(img_filename):
            os.remove(img_filename)
