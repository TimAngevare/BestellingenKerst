from django.core.validators import RegexValidator

snijd_validator = RegexValidator(r"(\d+:\d+,)+", "x aantal keer: (gewicht):(aantal),")
telnr_validator = RegexValidator(r"^\+316\d{8}$", "Moet beginnen met: +316")
tijdophalen_validator = RegexValidator(r"^\d{4}$", "format: 1330")

from django import forms
from django.utils.safestring import mark_safe

TYPE_OPTION = (
    ("standaard", "Standaard"),
    ("snijdvlees", "Snijdbaar vlees"),
    ("menu", "Menu"),
    ("gourmet", "Gourmet"),
    ("dryaged", "Dry Aged Vlees"),
)

# FORMAAT_OPTION = (
#     ('klein', 'Klein'),
#     ('groot', 'Groot'),
# )

DAGEN_OPHALEN_OPTION = [
    ('23', '23-12'),
    ('24', '24-12'),
    ('25', '25-12')
]

# FORMAAT_PROD_OPTION = (
#     ('de_tapas_plank', 'De Tapas Plank'),
#     ('de_party_pan', 'De Party Pan'),
# )

MENU_OPTION = (
    ('dorpsslagers_kerstmenu', 'Het Dorpsslagers Kerstmenu'),
    ('traditioneel_kerstmenu', 'Het Traditioneel Kerstmenu'),
)

SOORT_OPTION = (
    ('ribeye', 'Ribeye'),
    ('entrecote', 'Entrecote'),
    ('cote_a_los', "Cote a L'os"),
)

DRYAGED_OPTION = (
    ('blonde_aquitaine', 'Blonde Aquitaine'),
    ('france_limousine', 'France Limousin'),
    ('spaanse_rubia_gallega', 'Spaanse Rubia Gallega'),
)


def standaard_aantal(prod_label):
    return forms.IntegerField(label=mark_safe(prod_label),
                              min_value=0,
                              widget=forms.NumberInput(
                                  attrs={'class': 'w3-input w3-border w3-light-grey', 'value': '0'}
                              ))


temp_product = forms.CharField(label="Product",
                               max_length=100,
                               widget=forms.TextInput(
                                   attrs={'class': 'w3-input w3-border w3-light-grey', 'list': 'products'}
                               ))

temp_bijz = forms.CharField(label="Bijzonderheden",
                            max_length=200,
                            required=False,
                            widget=forms.TextInput(
                                attrs={'class': 'w3-input w3-border w3-light-grey'}
                            ))

temp_prod_type = forms.ChoiceField(label=mark_safe("<br />Type volgende product"),
                                   choices=TYPE_OPTION,
                                   widget=forms.Select(
                                       attrs={'class': 'w3-select'}
                                   ))

temp_aantal = forms.IntegerField(label="Aantal",
                                 min_value=1,
                                 widget=forms.NumberInput(
                                     attrs={'class': 'w3-input w3-border w3-light-grey'}
                                 ))

temp_gewicht = forms.IntegerField(label="Gewicht",
                                  min_value=0,
                                  widget=forms.NumberInput(
                                      attrs={'class': 'w3-input w3-border w3-light-grey'}
                                  ))


class NieuweBestellingForm(forms.Form):
    prod_type = temp_prod_type
    usr_email = forms.EmailField(label="E-mail adres", max_length=100,
                                 widget=forms.EmailInput(attrs={'class': 'w3-input w3-border w3-light-grey'}))
    dagophalen = forms.ChoiceField(label="Dag ophalen", choices=DAGEN_OPHALEN_OPTION, widget=forms.RadioSelect())


class BestellingAfmakenForm(forms.Form):
    naam = forms.CharField(label="Naam", max_length=150,
                           widget=forms.TextInput(attrs={'class': 'w3-input w3-border w3-light-grey'}))
    telnr = forms.CharField(label="Telefoon nummer", max_length=12, validators=[telnr_validator],
                            widget=forms.TextInput(
                                attrs={'class': 'w3-input w3-border w3-light-grey', 'value': '+316'}))
    tijdophalen = forms.CharField(label="Tijd ophalen", max_length=5, validators=[tijdophalen_validator],
                                  widget=forms.TextInput(attrs={'class': 'w3-input w3-border w3-light-grey'}))
    prod_type = temp_prod_type


class ProductForm(forms.Form):
    product = temp_product
    cat = forms.CharField(label="Categorie", max_length=100, widget=forms.TextInput(
        attrs={'class': 'w3-input w3-border w3-light-grey'}))


class SnijdForm(forms.Form):
    product = temp_product
    gewicht = temp_gewicht
    snijden = forms.CharField(label="Snijden", max_length=100, validators=[snijd_validator],
                              widget=forms.TextInput(attrs={'class': 'w3-input w3-border w3-light-grey'}))

    bijz = temp_bijz
    prod_type = temp_prod_type


class MenuForm(forms.Form):
    product = forms.ChoiceField(label="Product", choices=MENU_OPTION, widget=forms.Select(attrs={'class': 'w3-select'}))
    aantal = temp_aantal
    # cat = "menu"

    carpaccio = standaard_aantal("<br />(V-gerecht) Carpaccio")
    vitello_tonato = standaard_aantal("(V-gerecht) Vitello tonato")
    kalfsragout = standaard_aantal("(V-gerecht) Kalfsragout")
    biefstuk = standaard_aantal("(H-gerecht) Biefstuk")
    varkenshaas = standaard_aantal("(H-gerecht) Varkenshaas")
    tiramisu = standaard_aantal("(Dessert) Tiramisu")
    apfelstrudel = standaard_aantal("(Dessert) Apfelstrudel")

    bijz = temp_bijz
    prod_type = temp_prod_type


class GourmetForm(forms.Form):
    # cat = "zelf_gourmet"

    bavette = standaard_aantal("<br />Bavette")
    kogel_biefstuk = standaard_aantal("Kogel Biefstuk")
    ossenhaaspuntjes = standaard_aantal("Ossenhaaspuntjes")
    ba_hamburgers = standaard_aantal("Black Angus Hamburgers")
    rundervink = standaard_aantal("Rundervink")
    speklapjes = standaard_aantal("Speklapjes")
    varkenshaassate = standaard_aantal("Varkenshaassate")
    shoarma = standaard_aantal("Shoarma")
    varkenshaas = standaard_aantal("Varkenshaas")
    kip_bacon_chili = standaard_aantal("Kip Bacon Chili")
    slavink = standaard_aantal("Slavink")
    kipfilet = standaard_aantal("Kipfilet")
    hamburger = standaard_aantal("Hamburger")
    lamsrack = standaard_aantal("Lamsrack")
    dry_aged = standaard_aantal("Dry Aged")
    kalfsoester = standaard_aantal("Kalfsoester")
    diamanthaas = standaard_aantal("Diamanthaas")
    ba_cheddar = standaard_aantal("Black Angus Cheddar")
    chipolata = standaard_aantal("Chipolata")
    chinese_roaststeak = standaard_aantal("Chinese Roaststeak")

    bijz = temp_bijz
    prod_type = temp_prod_type


class DryAgedForm(forms.Form):
    product = forms.ChoiceField(label="Product", choices=DRYAGED_OPTION,
                                widget=forms.Select(attrs={'class': 'w3-select'}))
    soort = forms.ChoiceField(label="Soort", choices=SOORT_OPTION, widget=forms.Select(attrs={'class': 'w3-select'}))
    # cat = "dryaged"
    gewicht = temp_gewicht

    bijz = temp_bijz
    prod_type = temp_prod_type


class StandaardForm(forms.Form):
    product = temp_product
    aantal = temp_aantal

    bijz = temp_bijz
    prod_type = temp_prod_type
