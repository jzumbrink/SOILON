from .models import Bodenprobe, Auftrag, Kunde, GeoCoordinate, PpmValue
from .database_operations import get_ppm_value, get_customer_id
from .backend_calculations import convert_std_to_full_geo
import json


def get_geo_coordinates(soil_sample: Bodenprobe) -> tuple:
    if soil_sample.geo_coordinate_id == -1:
        return '', ''
    geo_obj: GeoCoordinate = GeoCoordinate.objects.get(id=soil_sample.geo_coordinate_id)
    return map(float, convert_std_to_full_geo(geo_obj.latitude, geo_obj.longitude).split(','))


def generate_data_soil_samples_json_file(path):
    all_soil_samples = Bodenprobe.objects.all()
    data = {
        'soilSamples': []
    }
    for soil_sample in all_soil_samples:
        latitude, longitude = get_geo_coordinates(soil_sample)
        data['soilSamples'].append({
            'customerId': get_customer_id(soil_sample),
            'cd': get_ppm_value('cd', soil_sample.id, int_std=True),
            'pb': get_ppm_value('pb', soil_sample.id, int_std=True),
            'cu': get_ppm_value('cu', soil_sample.id, int_std=True),
            'zn': get_ppm_value('zn', soil_sample.id, int_std=True),
            'cr': get_ppm_value('cr', soil_sample.id, int_std=True),
            'ni': get_ppm_value('ni', soil_sample.id, int_std=True),
            'as': get_ppm_value('as', soil_sample.id, int_std=True),
            'latitude': latitude,
            'longitude': longitude,
        })
    with open(path, 'w+') as file:
        json.dump(data, file, indent=4)
        return True
