from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from .models import Bodenprobe, PpmValue, Auftrag, Kunde


def get_ppm_value(element: str, soil_sample_id: int, int_std: bool = False):
    try:
        return PpmValue.objects.filter(
            bodenprobe_id=soil_sample_id,
            element=element
        )[0].value
    except IndexError:
        # no data available so far
        return -1 if int_std else '/'


def get_customer_id(soil_sample: Bodenprobe) -> int:
    try:
        return Kunde.objects.get(id=Auftrag.objects.get(id=soil_sample.auftrags_id).kunden_id).id
    except (ObjectDoesNotExist, MultipleObjectsReturned):
        # either no object or too many objects to perform the task correctly
        return -1
