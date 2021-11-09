from django import forms
from django.utils.safestring import mark_safe

TYPE_OPTION = (
    ("standaard", "Standaard"),
    ("snijdvlees", "Snijdbaar vlees"),
    ("menu", "Menu"),
    ("gourmet", "Gourmet"),
    ("dryaged", "Dry Aged Vlees"),
)

class Bestellingen(forms.Form):
    bestel_nmr = forms.IntegerField(required=False, min_value=1, max_value=3000)
    dag_ophalen = forms.IntegerField(required=False, min_value=23, max_value=25)
    tel = forms.CharField(required=False, max_length=12, min_length=12)

class Producten(forms.Form):
    pass