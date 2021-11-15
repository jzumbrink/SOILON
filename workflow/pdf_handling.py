import tabula
import pandas
import csv
import os
import datetime
from .models import Kunde, PpmValue

def createCSVfromPDF(pdf_filename, csv_filename):
    tabula.convert_into(pdf_filename,
                        csv_filename,
                        output_format='csv',
                        pages=1
    )


def createExcelfromCSV(csv_filename, excel_filename):
    c = pandas.read_csv(csv_filename, encoding='ISO-8859-1')
    c.to_excel(excel_filename,
               index=None,
               header=True,
               sheet_name="Bodenprobe",
               encoding='ISO-8859-1',
    )


def getDictFromCSV(csv_filename):
    data = {}
    with open(csv_filename) as c:
        for line in csv.reader(c):
            content_list = line[2:]
            content_list.insert(0, line[0])
            data[line[1]] = content_list
    return data


def createCustomerTextFromBlueprint(blueprint_text, bodenprobe_daten, kundendaten):
    new_text = blueprint_text.format(
        kundendaten["anrede"],
        kundendaten["nachname"],
        bodenprobe_daten["Pb"][3],
        bodenprobe_daten["As"][3],
        bodenprobe_daten["Zn"][3],
        bodenprobe_daten["Cu"][3],
    )
    return new_text

def createFloatFromString(old_string):
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


def handle_bodenprobe_auswertung(pdf_file, kunden_id, auftrags_id, messung_id):
    #Kundendaten bekommen
    kundendaten = Kunde.objects.filter(pk=kunden_id).values('anrede', 'vorname', 'nachname')[0]
    # das richtige Verzeichnis erstellen falls noch nicht vorhanden
    try:
        os.mkdir("data/kunden-bodenproben-pdf/{0}".format(messung_id))
    except FileExistsError:
        # das Verzeichnis wurde schon erstellt
        pass
        #Error, da die ID nicht eindeutig wäre bzw. nach Anweisung fragen

    #kundendaten = {"Anrede": x, "Vorname": y, "Nachname":z}
    raw_data_path = 'data/kunden-bodenproben-pdf/{0}/'.format(messung_id)
    raw_filename = 'BPR-{0}-K{1}.A{2}.B{3}.'.format(datetime.datetime.now().strftime("%d.%m.%Y-%H.%M"), kunden_id, auftrags_id, messung_id)
    filename = raw_data_path+raw_filename
    with open(filename+"pdf", 'wb+') as file2:
        for c in pdf_file.chunks():
            file2.write(c)

    createCSVfromPDF(filename+'pdf', filename+'csv')
    createExcelfromCSV(filename+'csv', filename+'xlsx')
    daten = getDictFromCSV(filename+'csv')
    print(daten)
    # Für die Elemente die Daten als ppm-Value speichern (*10,000)
    for element_name in ['Cd', 'Cu', 'Pb', 'Zn']:
        ppm_value = createFloatFromString(daten[element_name][3])
        if len(PpmValue.objects.filter(bodenprobe_id=messung_id, element=element_name.lower())) == 0:
            #Falls es für die Bodenprobe noch keine PPmValue objects gibt, dann werden sie erstellt
            PpmValue.objects.create(
                bodenprobe_id=messung_id,
                element=element_name.lower(),
                value=ppm_value,
            )
        else:
            # Ansonsten werden die PpmValue geupdated
            PpmValue.objects.filter(bodenprobe_id=messung_id, element=element_name.lower()).update(value=ppm_value)

    kundentext = open("etc/txt_t/kundennachricht_auswertung_t.txt", encoding="utf-8", mode="r").read()
    new_text = createCustomerTextFromBlueprint(kundentext, daten, kundendaten)
    print(new_text)

    # die csv-Datei löschen
    os.remove(filename+"csv")

    return new_text, raw_data_path, raw_filename
