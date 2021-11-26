from django import forms
from django.utils.safestring import mark_safe

TYPE_OPTION = (
    ("standaard", "Standaard"),
    ("snijdvlees", "Snijdbaar vlees"),
    ("menu", "Menu"),
    ("gourmet", "Gourmet"),
    ("dryaged", "Dry Aged Vlees"),
)
TYPE_DAY = (
    (23, 23),
    (24, 24),
    (25, "Alles")
)
TYPE_STATE = (
    (0 , "Niet gestart"),
    (1, "Bezig"),
    (2, "Klaar"),
    (3, "Problemen"),
    (4, "Alles")
)

class bestellingen(forms.Form):
    bestel_nmr = forms.IntegerField(required=False, min_value=1, max_value=30000)
    dag_ophalen = forms.IntegerField(required=False, min_value=23, max_value=25)
    tel = forms.CharField(required=False, max_length=12, min_length=12)

class producten(forms.Form):
    temp_prod_type = forms.ChoiceField(label=mark_safe("Type product"),
                                   choices=TYPE_OPTION,
                                   widget=forms.Select(
                                       attrs={'class': 'w3-select'}
                                   ))
    temp_product = forms.CharField(label="Product",
                               max_length=100,
                               required=False,
                               widget=forms.TextInput(
                                   attrs={'class': 'w3-input w3-border w3-light-grey', 'list': 'products'}
                               ))
class alles(forms.Form):
    dag = forms.ChoiceField(label=mark_safe("dag"),
                                   choices=TYPE_DAY,
                                   required=False,
                                   widget=forms.Select(
                                       attrs={'class': 'w3-select'}
                                   ))
    state = forms.ChoiceField(label=mark_safe("eigenschap"),
                                   choices=TYPE_STATE,
                                   required=True,
                                   widget=forms.Select(
                                       attrs={'class': 'w3-select'}
                                   ))