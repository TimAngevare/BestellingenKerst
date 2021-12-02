from django import forms
from django.utils.safestring import mark_safe
import mongo_manage

TYPE_OPTION = (
    ("menu", "Menu"),
    ("gourmet", "Gourmet"),
    ("dry_aged", "Dry Aged Vlees"),
    ("bbq", "BBQ"),
    ("bijgerecht", "Bijgerecht"),
    ("borrel", "Borrel"),
    ("dessert", "Dessert"),
    ("gevogelte", "Gevogelte"),
    ("hoofdgerecht", "Hoofdgerecht"),
    ("kalf", "Kalf"),
    ("koud_voorgerecht", "Koude voorgerechten"),
    ("lam", "Lam"),
    ("rollade", "Rollade"),
    ("rund", "Rund"),
    ("varken", "Varken"),
    ("wagyu", "Wagyu"),
    ("warm_voorgerecht", "Warme voorgerechten"),
    ("wild", "Wild"),
    ("zelf_gourmet", "Zelf Gourmet"),
    ("anders", "overig")
)

TYPE_DAY = (
    (23, 23),
    (24, 24),
    (25, "Alles")
)
TYPE_STATE = (
    ("niet_gestart" , "Niet gestart"),
    ("bezig", "Bezig"),
    ("voltooid", "Klaar"),
    ("probleem", "Problemen"),
    ("Alles", "Alles")
)

class bestellingen(forms.Form):
    bestel_nmr = forms.IntegerField(required=False, min_value=1, max_value=30000)
    dag_ophalen = forms.IntegerField(required=False, min_value=23, max_value=25)
    tel = forms.CharField(required=False, max_length=12, min_length=12)
    naam = forms.CharField(required=False, min_length=3)

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
                                   attrs={'class': 'w3-input w3-border w3-light-grey', 'list': 'products', 'spellcheck' : 'false'}
                               ))
    state = forms.ChoiceField(label=mark_safe("eigenschap"),
                                   choices=TYPE_STATE,
                                   required=True,
                                   widget=forms.Select(
                                       attrs={'class': 'w3-select'}
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