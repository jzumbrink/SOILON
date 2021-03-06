from django import forms
from .config import soil_sample_price, std_auftrag_name
from .models import Bodenprobe


class ChooseOrder(forms.Form):
    auftrags_id = forms.IntegerField(
        widget=forms.NumberInput,
    )


class UploadPdfBodenprobeFile(forms.Form):
    pdf_bodenprobe_file = forms.FileField()
    bodenprobe_id = None

    def __init__(self, auftrag_id, *args, **kwargs):
        super(UploadPdfBodenprobeFile, self).__init__(*args, **kwargs)
        self.fields['bodenprobe_id'] = forms.ModelChoiceField(
            queryset=Bodenprobe.objects.filter(auftrags_id=auftrag_id),
            widget=forms.Select,
        )

    class Meta:
        model = Bodenprobe


class NewOrder(forms.Form):
    kunden_id = forms.IntegerField(widget=forms.NumberInput, min_value=0)
    anzahl_bodenproben = forms.IntegerField(widget=forms.NumberInput, initial=1, min_value=1)
    preis = forms.FloatField(initial=soil_sample_price,
                             widget=forms.NumberInput(
                                 attrs={
                                     'step': 0.01,
                                 }
                             ))
    payment_received = forms.BooleanField(required=False,
                                          widget=forms.CheckboxInput
                                          )
    custom_name = forms.CharField(widget=forms.TextInput,
                                  initial=std_auftrag_name)
    extra_info = forms.CharField(required=False,
                                 widget=forms.Textarea)


geschlecht = [
    ('d', 'Divers'),
    ('w', 'Weiblich'),
    ('m', 'Männlich'),
]


class NewCustomer(forms.Form):

    vorname = forms.CharField(min_length=2, max_length=50)
    nachname = forms.CharField(min_length=2, max_length=50)
    geschlecht = forms.ChoiceField(
        choices=geschlecht,
        required=False,
    )
    titel = forms.CharField(required=False)
    email = forms.EmailField(max_length=50)
    telefonnummer = forms.IntegerField()
    land = forms.CharField(
        max_length=40,
        initial="Deutschland",
    )
    plz = forms.IntegerField(
        min_value=1067, # Niedrigste Postleitzahl: Dresden
        max_value=99998, # Höchste Postleitzahl: Thüringen
        widget=forms.NumberInput,
    )
    wohnort = forms.CharField(max_length=50)
    strasse = forms.CharField(max_length=100)
    hausnummer = forms.CharField(
        max_length=10,
    )
    adresszusatz = forms.CharField(required=False)


class UpdateAuftrag(forms.Form):

    bereits_gezahlt = forms.BooleanField(required=True,
                                         initial=False)


class UpdateSoilSample(forms.Form):
    # TODO intial value
    status_id = forms.IntegerField(
        min_value=0,
        max_value=6,
        required=False
    )

    is_billing_address_sampling_point = forms.BooleanField(required=False)

    alt_zip_code = forms.IntegerField(required=False)
    alt_city = forms.CharField(max_length=50, required=False)
    alt_street = forms.CharField(max_length=100, required=False)
    alt_house_number = forms.CharField(max_length=10, required=False)
    alt_country = forms.CharField(max_length=40, initial="Deutschland", required=False)
    alt_address_suffix = forms.CharField(max_length=100, required=False)

    geographic_coordinates_full_field = forms.CharField(required=False,
                                                        widget=forms.TextInput(attrs={'placeholder': 'hier die Koordinaten einfügen'}))

    from_duisburg_south = forms.BooleanField(required=False, initial=False)
