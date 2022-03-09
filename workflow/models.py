from django.db import models
from .config import bodenprobe_preis


class Kunde(models.Model):
    # kunden_id wird als Integer Wert automatisch von Django erstellt
    # dabei ist der primary_key dann read only

    nachname = models.CharField(max_length=50)  # required
    vorname = models.CharField(max_length=50)  # required
    plz = models.IntegerField(blank=True)
    wohnort = models.CharField(max_length=50, blank=True)
    strasse = models.CharField(max_length=100, blank=True)
    hausnummer = models.CharField(max_length=10, blank=True, null=True)
    land = models.CharField(max_length=40, default="Deutschland")
    adresszusatz = models.CharField(max_length=100, blank=True)
    telefonnummer = models.IntegerField(blank=True, null=True)
    email = models.CharField(max_length=50, blank=True)
    update_emails = models.BooleanField(default=False)
    geburtstag = models.DateField(blank=True, null=True)
    registrierungs_zeit = models.DateTimeField()
    geschlecht = models.CharField(max_length=20, default="nicht angegeben")
    titel = models.CharField(max_length=20, blank=True)
    anrede = models.CharField(max_length=20, default="Frau/Herr")

    def __str__(self):
        return self.nachname + ', ' + self.vorname + ' (' + str(self.id) + ')'


def getFilename(instance, filename):
    return "bodenproben/{0}".format(filename)


class Auftrag(models.Model):
    kunden_id = models.IntegerField()
    anzahl_bodenproben = models.IntegerField(default=1)
    notizen = models.TextField(blank=True)
    preis = models.FloatField(default=bodenprobe_preis)
    nachlass = models.FloatField(default=0)
    bereits_gezahlt = models.BooleanField(default=False)
    ergebnisse_zurueckgemeldet = models.IntegerField(default=0)
    label_name = models.CharField(max_length=50, blank=True)
    mail_auftrags_text = models.TextField(blank=True)
    status = models.CharField(max_length=50, default="Neuer Auftrag")
    eingangs_zeit = models.DateTimeField(null=True)

    def __str__(self):
        if self.label_name is None:
            return "Auftrag(Nr. " + str(self.id) + ")"
        return "Auftrag(Nr. " + str(self.id) + ") " + self.label_name


class Bodenprobe(models.Model):
    auftrags_id = models.IntegerField()
    pdf_original = models.FileField(
        upload_to=getFilename,
        default="*",
        blank=True,
    )
    pdf_auswertung_kunde = models.FileField(
        upload_to=getFilename,
        default="*",
        blank=True,
    )
    xlsx_auswertung = models.FileField(
        upload_to=getFilename,
        default="*",
        blank=True,
    )
    # TODO update Current State List
    """
    Current State List: (outdated)
    0: Auftrag ist gerade eingegangen -> Auftrag ins System richtig einbetten und Kundeninteraktion abwickeln
    1: Bodenprobe entnohmen/abwickelt
    2: Bodenprobe im Trockenschrank und fertig
    3: Probenaufbereitung fertig
    4: Analyse fertig
    5: Bezahlt und fertig abgewickelt
    """
    status = models.IntegerField(default=0)
    extra_info = models.TextField(blank=True)
    mail_text = models.TextField()
    label_name = models.CharField(max_length=50, default="Standard-Bodenprobe")

    raw_data_path = models.CharField(max_length=60, blank=True)
    raw_filename = models.CharField(max_length=60, blank=True)

    results_upload_time = models.DateTimeField(blank=True)

    is_billing_address_sampling_point = models.BooleanField(default=False)
    alt_sampling_point_address_id = models.IntegerField(blank=True, default=-1)

    geo_coordinate_id = models.IntegerField(blank=True, default=-1)

    from_duisburg_south = models.BooleanField(blank=True, default=False)

    def __str__(self):
        if self.label_name is None or self.label_name == '':
            return "Bodenprobe (Nr. " + str(self.id) + ")"
        return "Bodenprobe (Nr. " + str(self.id) + "): " + self.label_name


class Address(models.Model):
    zip_code = models.IntegerField(blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    street = models.CharField(max_length=100, blank=True, null=True)
    house_number = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=40, default="Deutschland", null=True)
    address_suffix = models.CharField(max_length=100, blank=True, null=True)


class PpmValue(models.Model):
    element = models.CharField(max_length=2)
    value = models.FloatField()
    bodenprobe_id = models.IntegerField()


class GeoCoordinate(models.Model):
    # Die Koordinaten werden mit 10^12 multipliziert und dann gespeichert
    # Breitengrad
    latitude = models.IntegerField()
    # Längengrad
    longitude = models.IntegerField()
