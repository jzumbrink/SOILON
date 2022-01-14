from .models import Bodenprobe, Kunde, GeoCoordinate
from django.shortcuts import get_object_or_404


def getPercentageKundendaten(kunde_id):
    try:
        kunde = Kunde.objects.filter(pk=kunde_id)[0]
        eingetragene_daten = 0
        daten_ges = 0
        for value in [kunde.vorname, kunde.nachname, kunde.plz, kunde.wohnort, kunde.strasse, kunde.hausnummer, kunde.land, kunde.telefonnummer, kunde.email, kunde.anrede]:
            if value is not None:
                eingetragene_daten += 1
            daten_ges += 1
        return int((eingetragene_daten / daten_ges) * 100)
    except IndexError:
        return 0


def getPercentageAuftragBodenproben(auftrag_id, status_match_arr):
    bodenproben_hochgeladen = 0
    bodenproben_ges = 0
    for bodenprobe in Bodenprobe.objects.filter(auftrags_id=auftrag_id):
        if bodenprobe.status in status_match_arr:
            # Falls die Bodenprobe schon analysiert wurde, bzw. ein pdf-Dokument dazu vorliegt oder
            # der Vorgang schon bezahlt und abgewickelt wurde, dann wird die Bodenprobe als completed vermerkt
            bodenproben_hochgeladen += 1
        bodenproben_ges += 1

    # Die Prozentzahl der fertigen Bodenproben an der Gesamtzahl zurückgeben
    try:
        return int((bodenproben_hochgeladen / bodenproben_ges) * 100)
    except ZeroDivisionError:
        return 0


def getComparisionScore(search_string, db_obj, search_fields=[]):
    #Simpler Suchalgorithmus, der ein Suchword mit Elementen aus dem Objekt Kunde vergleicht
    #Zur Reduzierung der Komplexität und Minimierung des Rechenaufwands handelt es sich hierbei lediglich um lineares
    #Vergleichen.
    #Das heißt, dass immer nur benachbarte Buchstaben miteinander verglichen werden und nicht etwa Teile von Wörtern,
    #die an unterschiedlicher Stelle stehen.
    score_ges = []
    compare_list = []
    for search_field in search_fields:
        search_field = search_field.split('+')
        s = []
        for sf in search_field:
            s.append(str(db_obj.__dict__.get(sf)))
        compare_list.append(s)
    for comp_value in compare_list:
        value = " ".join(comp_value)
        score = 0
        for i in range(len(value)):
            if i < len(search_string):
                if value[i] == search_string[i]:
                    #Gleicher Buchstabe
                    score += 1;continue
                if value[i].lower() == search_string[i].lower():
                    #gleicher Buchstabe, nur Groß-Kleinschreibung anders
                    score += 0.93
            if i > 0 and i - 1 < len(search_string):
                if value[i] == search_string[i - 1]:
                    score += 0.7;continue
                if value[i].lower() == search_string[i - 1].lower():
                    score += 0.65;continue
            if i + 1 < len(search_string):
                if value[i] == search_string[i + 1]:
                    score += 0.7;continue
                if value[i].lower() == search_string[i + 1].lower():
                    score += 0.65;continue
        if len(value) != len(search_string):
            score *= 0.7 + (0.28 / abs(len(value) - len(search_string)))
        if len(value) > 0:
            score_ges.append(score / len(search_string))
    return max(score_ges)


def convert_std_to_full_geo(latitude: int, longitude: int):
    return ', '.join([str(float(value)*10**(-12)) for value in [latitude, longitude]])


def convert_full_geo_to_std(full_geo_coordinate: str):
    return [int(float(coordinate.rstrip())*10**12) for coordinate in full_geo_coordinate.split(',')]


def save_full_geo_coordinate(soil_sample_id: int, full_geo_coordinate: str):
    soil_sample = get_object_or_404(Bodenprobe, pk=soil_sample_id)
    latitude, longitude = convert_full_geo_to_std(full_geo_coordinate)
    if soil_sample.geo_coordinate_id < 0:
        # create new geo_coordinate
        geo_coordinate = GeoCoordinate.objects.create(
            latitude=latitude,
            longitude=longitude,
        )
        Bodenprobe.objects.filter(pk=soil_sample_id).update(geo_coordinate_id=geo_coordinate.id)
    else:
        GeoCoordinate.objects.filter(pk=soil_sample.geo_coordinate_id).update(
                                     latitude=latitude,
                                     longitude=longitude
                                     )


def get_full_geo_coordinate(soil_sample_id: int):
    soil_sample = get_object_or_404(Bodenprobe, pk=soil_sample_id)
    if soil_sample.geo_coordinate_id < 0:
        return ''
    geo_coordinate = get_object_or_404(GeoCoordinate, pk=soil_sample.geo_coordinate_id)
    return convert_std_to_full_geo(geo_coordinate.latitude, geo_coordinate.longitude)
