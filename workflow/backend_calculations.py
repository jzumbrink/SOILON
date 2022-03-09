from .models import Bodenprobe, Kunde, GeoCoordinate
from django.shortcuts import get_object_or_404


def get_percentage_customer_data(customer_id: int):
    try:
        customer = Kunde.objects.filter(pk=customer_id)[0]
        entered_data = 0
        data_total = 0
        for value in [customer.vorname,
                      customer.nachname,
                      customer.plz,
                      customer.wohnort,
                      customer.strasse,
                      customer.hausnummer,
                      customer.land,
                      customer.telefonnummer,
                      customer.email,
                      customer.anrede]:
            if value is not None:
                entered_data += 1
            data_total += 1
        return int((entered_data / data_total) * 100)
    except IndexError:
        return 0


def getPercentageAuftragBodenproben(order_id: int, status_match_arr: list):
    soil_samples_uploaded: int = 0
    soil_samples_total: int = 0
    for soil_sample in Bodenprobe.objects.filter(auftrags_id=order_id):
        if soil_sample.status in status_match_arr:
            # if the soil sample is yet analyzed and a pdf document could be created
            # and if the sample is already payed, then the soil sample will be marked as completed/uploaded
            soil_samples_uploaded += 1
        soil_samples_total += 1

    # return the percentage of the completed soil samples in relation to the total number of soil samples
    try:
        return int((soil_samples_uploaded / soil_samples_total) * 100)
    except ZeroDivisionError:
        return 0


def get_comparision_score(search_string, db_obj, search_fields=[]):
    # simple search algorithm, which compares a searchword with elements from the object Kunde
    # to reduce complexity and to minimize the computation time the algorithm only uses linear comparision
    # it means, that only adjacent letters are compared to each other
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
                    # same letter
                    score += 1
                    continue
                if value[i].lower() == search_string[i].lower():
                    # same letter, but case is different
                    score += 0.93
            if i > 0 and i - 1 < len(search_string):
                if value[i] == search_string[i - 1]:
                    score += 0.7
                    continue
                if value[i].lower() == search_string[i - 1].lower():
                    score += 0.65
                    continue
            if i + 1 < len(search_string):
                if value[i] == search_string[i + 1]:
                    score += 0.7
                    continue
                if value[i].lower() == search_string[i + 1].lower():
                    score += 0.65
                    continue
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
    if len(full_geo_coordinate) > 0:
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
    else:
        # delete Coordinate
        GeoCoordinate.objects.filter(pk=soil_sample.geo_coordinate_id).delete()
        Bodenprobe.objects.filter(pk=soil_sample_id).update(geo_coordinate_id=-1)


def get_full_geo_coordinate(soil_sample_id: int):
    soil_sample = get_object_or_404(Bodenprobe, pk=soil_sample_id)
    if soil_sample.geo_coordinate_id < 0:
        return ''
    geo_coordinate = get_object_or_404(GeoCoordinate, pk=soil_sample.geo_coordinate_id)
    return convert_std_to_full_geo(geo_coordinate.latitude, geo_coordinate.longitude)
