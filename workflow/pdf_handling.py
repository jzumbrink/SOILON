import tabula
import pandas
import csv
import os
import datetime
from .config import relevant_elements
from .models import Kunde, PpmValue


def create_csv_from_pdf(pdf_filename: str, csv_filename: str):
    tabula.convert_into(pdf_filename,
                        csv_filename,
                        output_format='csv',
                        pages=1
                        )


def create_excel_from_csv(csv_filename: str, excel_filename: str):
    c = pandas.read_csv(csv_filename, encoding='ISO-8859-1')
    c.to_excel(excel_filename,
               index=None,
               header=True,
               sheet_name="Bodenprobe",
               encoding='ISO-8859-1',
               )


def get_dict_from_csv(csv_filename: str) -> dict:
    data = {}
    with open(csv_filename) as c:
        for line in csv.reader(c):
            content_list = line[2:]
            content_list.insert(0, line[0])
            data[line[1]] = content_list
    return data


def create_customer_text_from_blueprint(blueprint_text: str, soil_sample_data, customer_data) -> str:
    new_text = blueprint_text.format(
        customer_data["anrede"],
        customer_data["nachname"],
        soil_sample_data["Pb"][3],
        soil_sample_data["As"][3],
        soil_sample_data["Zn"][3],
        soil_sample_data["Cu"][3],
    )
    return new_text


def create_float_from_string(old_string: str) -> float:
    new_string = ""
    for char in old_string:
        if char == ",":
            new_string += "."
        elif char in [str(i) for i in range(10)]:
            new_string += char
    # Wird noch gerundet, da die Maschine nur bis eine Nachkommastelle bei ppm analysiert
    # Es treten aber gelegentlich beim Umrechnen in ein float Ungenauigkeiten im Bereich ca. 10*-10 auf. Diese sollten
    # jedoch ignoriert werden, da sie nicht das reele Ergebnis wiedergeben
    return round(float(new_string) * 10000, 1)


def handle_soil_sample_evaluation(pdf_file, customer_id: int, order_id: int, soil_sample_id: int):
    customer_data: dict = Kunde.objects.filter(pk=customer_id).values('anrede', 'vorname', 'nachname')[0]
    # create the correct folder if not yet existent
    try:
        os.mkdir("data/kunden-bodenproben-pdf/{0}".format(soil_sample_id))
    except FileExistsError:
        # the folder already exists
        pass
        # Error, da die ID nicht eindeutig wäre bzw. nach Anweisung fragen

    # customer_data = {"Anrede": x, "Vorname": y, "Nachname":z}
    raw_data_path: str = 'data/kunden-bodenproben-pdf/{0}/'.format(soil_sample_id)
    raw_filename: str = 'BPR-{0}-K{1}.A{2}.B{3}.'.format(datetime.datetime.now().strftime("%d.%m.%Y-%H.%M"), customer_id,
                                                    order_id, soil_sample_id)
    filename: str = raw_data_path + raw_filename
    with open(filename + "pdf", 'wb+') as file2:
        for c in pdf_file.chunks():
            file2.write(c)

    create_csv_from_pdf(filename + 'pdf', filename + 'csv')
    create_excel_from_csv(filename + 'csv', filename + 'xlsx')
    data = get_dict_from_csv(filename + 'csv')
    # save the data as ppm-value (multiply by 10,000)
    for element_name in relevant_elements:
        ppm_value = create_float_from_string(data[element_name][3])
        if len(PpmValue.objects.filter(bodenprobe_id=soil_sample_id, element=element_name.lower())) == 0:
            # if there are not any PpmValue object for the soil sample, then they will be created
            PpmValue.objects.create(
                bodenprobe_id=soil_sample_id,
                element=element_name.lower(),
                value=ppm_value,
            )
        else:
            # otherwise the PpmValue object will be updated
            PpmValue.objects.filter(bodenprobe_id=soil_sample_id, element=element_name.lower()).update(value=ppm_value)

    kundentext = open("etc/txt_t/kundennachricht_auswertung_t.txt", encoding="utf-8", mode="r").read()
    new_text = create_customer_text_from_blueprint(kundentext, data, customer_data)

    # remove the csv file, because it is no longer needed
    os.remove(filename + "csv")

    return new_text, raw_data_path, raw_filename
