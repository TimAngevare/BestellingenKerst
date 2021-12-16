from django.core.validators import RegexValidator

snijd_validator = RegexValidator(r"(\d+:\d+,)+", "x aantal keer: (gewicht):(aantal),")
telnr_validator = RegexValidator(r"^\+316\d{8}$", "Moet beginnen met: +316")
tijdophalen_validator = RegexValidator(r"^\d{4}$", "format: 1330")

from django import forms
from django.utils.safestring import mark_safe

TYPE_OPTION = (
    ("standaard", "Standaard"),
    ("snijdvlees", "Snijdbaar vlees"),
    ("menu", "Traditioneel Kerstmenu"),
    ("zelf_gourmet", "Gourmet"),
    ("dry_aged", "Dry Aged Vlees"),
    ("rollade", "Rollade"),
)

DAGEN_OPHALEN_OPTION = [
    ('23', '23-12'),
    ('24', '24-12'),
    ('25', '25-12'),
    ('26', '26-12')
]

SOORT_OPTION = (
    ('cote a los', "Cote a L'os"),
    ('entrecote', 'Entrecote'),
    ('ribeye', 'Ribeye'),
)

DRYAGED_OPTION = (
    ('australisch_angus', 'Australisch Angus'),
    ('black_angus', 'Black Angus'),
    ('blonde_aquitaine', 'Blonde Aquitaine'),
    ('france_limousin', 'France Limousin'),
    ('friese_holsteiner', 'Friese Holsteiner'),
    ('schotse_aberdeen_angus', 'Schotse Aberdeen Angus'),
    ('simmentaler_oostenrijk', 'Simmentaler Oostenrijk'),
    ('spaanse_rubia_gallega', 'Spaanse Rubia Gallega'),
    ('west_vlaams_rood', 'West Vlaams Rood'),
)

ROLLADE_OPTION = (
    ('buikspek_rollade', 'Buikspek Rollade'),
    ('half_om_half_rollade', 'Half om Half Rollade'),
    ('kalfslende_rollade', 'Kalfslende Rollade'),
    ('kalkoendij_rollade', 'Kalkoendij Rollade'),
    ('kip_rollade', 'Kip Rollade'),
    ('lamsbilletje_rollade', 'Lamsbilletje Rollade'),
    ('rollade_van_het_staartstuk', 'Rollade van het Staartstuk'),
    ('runderlende_rollade', 'Runderlende Rollade'),
    ('runderstoof_rollade', 'Runderstoof Rollade'),
    ('varkensfilet_rollade', 'Varkensfilet Rollade'),
    ('varkensschouder_rollade', 'Varkensschouder Rollade'),
)


def standaard_aantal(prod_label):
    return forms.IntegerField(label=mark_safe(prod_label),
                              min_value=0,
                              widget=forms.NumberInput(
                                  attrs={'class': 'w3-input w3-border w3-light-grey', 'value': '0'}
                              ))


def standaard_mar(prod_label):
    return forms.BooleanField(label=mark_safe(prod_label), required=False)


temp_product = forms.CharField(label="Product",
                               max_length=100,
                               widget=forms.TextInput(
                                   attrs={'class': 'w3-input w3-border w3-light-grey',
                                          'list': 'products',
                                          'spellcheck': 'false'}
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
    medewerker = forms.CharField(label=mark_safe("<br />Medewerker"),
                                 widget=forms.TextInput(attrs={'class': 'w3-input w3-border w3-light-grey'}))

    # def __init__(self, *args, request=None, **kwargs):
    #     super(NieuweBestellingForm, self).__init__(*args, **kwargs)
    #     if request is not None:
    #         try:
    #             self.fields['medewerker'].value = request.COOKIES['fav_medewerker']
    #         except KeyError:
    #             pass


class BestellingAfmakenForm(forms.Form):
    naam = forms.CharField(label="Naam", max_length=150,
                           widget=forms.TextInput(attrs={'class': 'w3-input w3-border w3-light-grey'}))
    telnr = forms.CharField(label="Telefoon nummer", max_length=12, validators=[telnr_validator],
                            widget=forms.TextInput(
                                attrs={'class': 'w3-input w3-border w3-light-grey', 'value': '+316'}))
    tijdophalen = forms.CharField(label="Tijd ophalen", max_length=5, validators=[tijdophalen_validator],
                                  widget=forms.TextInput(attrs={'class': 'w3-input w3-border w3-light-grey'}))


class ProductForm(forms.Form):
    product = temp_product
    cat = forms.CharField(label="Categorie", max_length=100, widget=forms.TextInput(
        attrs={'class': 'w3-input w3-border w3-light-grey',
               'list': 'cats',
               'spellcheck': 'false'
               }))

    snijdvlees = forms.BooleanField(label="Snijdbaar vlees", required=False, widget=forms.CheckboxInput(
        attrs={'class': 'w3-check'}
    ))


class SpecialeOptieForm(forms.Form):
    prod_type = temp_prod_type


class SnijdForm(forms.Form):
    product = temp_product
    gewicht = temp_gewicht
    snijden = forms.CharField(label="Snijden", max_length=100, validators=[snijd_validator],
                              widget=forms.TextInput(attrs={'class': 'w3-input w3-border w3-light-grey'}))

    bijz = temp_bijz
    prod_type = temp_prod_type


class MenuForm(forms.Form):
    # product = forms.ChoiceField(label="Product", choices=MENU_OPTION, widget=forms.Select(attrs={'class': 'w3-select'}))
    aantal = temp_aantal
    # cat = "menu"

    carpaccio = standaard_aantal("<br />(V-gerecht) Carpaccio")
    kalfsragout = standaard_aantal("(V-gerecht) Kalfsragout")

    bijz = temp_bijz
    prod_type = temp_prod_type


class GourmetForm(forms.Form):
    # cat = "zelf_gourmet"

    ba_cheddar = standaard_aantal("<br />Black Angus Cheddar")
    ba_cheddar_mar = standaard_mar("Black Angus Cheddar gemarineerd")

    ba_hamburgers = standaard_aantal("<br />Black Angus Hamburgers")
    ba_hamburgers_mar = standaard_mar("Black Angus gemarineerd")

    bavette = standaard_aantal("<br />Bavette")
    bavette_mar = standaard_mar("Bavette gemarineerd")

    chinese_roaststeak = standaard_aantal("<br />Chinese Roaststeak")
    chinese_roaststeak_mar = standaard_mar("Chinese Roaststeak gemarineerd")

    chipolata = standaard_aantal("<br />Chipolata")
    chipolata_mar = standaard_mar("Chipolata gemarineerd")

    diamanthaas = standaard_aantal("<br />Diamanthaas")
    diamanthaas_mar = standaard_mar("Diamanthaas gemarineerd")

    dry_aged = standaard_aantal("<br />Dry Aged")
    dry_aged_mar = standaard_mar("Dry Aged gemarineerd")

    hamburger = standaard_aantal("<br />Hamburger")
    hamburger_mar = standaard_mar("Hamburger gemarineerd")

    kalfsoester = standaard_aantal("<br />Kalfsoester")
    kalfsoester_mar = standaard_mar("Kalfsoester gemarineerd")

    kip_bacon_chili = standaard_aantal("<br />Kip Bacon Chili")
    kip_bacon_chili_mar = standaard_mar("Kip Bacon Chili gemarineerd")

    kipfilet = standaard_aantal("<br />Kipfilet")
    kipfilet_mar = standaard_mar("Kipfilet gemarineerd")

    kogel_biefstuk = standaard_aantal("<br />Kogel Biefstuk")
    kogel_biefstuk_mar = standaard_mar("Kogel Biefstuk gemarineerd")

    lamsrack = standaard_aantal("<br />Lamsrack")
    lamsrack_mar = standaard_mar("Lamsrack gemarineerd")

    ossenhaaspuntjes = standaard_aantal("<br />Ossenhaaspuntjes")
    ossenhaaspuntjes_mar = standaard_mar("Ossenhaaspuntjes gemarineerd")

    rundervink = standaard_aantal("<br />Rundervink")
    rundervink_mar = standaard_mar("Rundervink gemarineerd")

    shoarma = standaard_aantal("<br />Shoarma")
    shoarma_mar = standaard_mar("Shoarma gemarineerd")

    slavink = standaard_aantal("<br />Slavink")
    slavink_mar = standaard_mar("Slavink gemarineerd")

    speklapjes = standaard_aantal("<br />Speklapjes")
    speklapjes_mar = standaard_mar("Speklapjes gemarineerd")

    varkenshaas = standaard_aantal("<br />Varkenshaas")
    varkenshaas_mar = standaard_mar("Varkenshaas gemarineerd")

    varkenshaassate = standaard_aantal("<br />Varkenshaassate")
    varkenshaassate_mar = standaard_mar("Varkenshaassate gemarineerd")

    bijz = temp_bijz
    prod_type = temp_prod_type


class DryAgedForm(forms.Form):
    product = forms.ChoiceField(label="Product", choices=DRYAGED_OPTION,
                                widget=forms.Select(attrs={'class': 'w3-select'}))
    soort = forms.ChoiceField(label="Soort", choices=SOORT_OPTION, widget=forms.Select(attrs={'class': 'w3-select'}))
    # cat = "dry_aged"
    gewicht = temp_gewicht

    bijz = temp_bijz
    prod_type = temp_prod_type


class StandaardForm(forms.Form):
    product = temp_product
    aantal = temp_aantal

    bijz = temp_bijz
    prod_type = temp_prod_type


class RolladeForm(forms.Form):
    product = forms.ChoiceField(label="Product", choices=ROLLADE_OPTION,
                                widget=forms.Select(attrs={'class': 'w3-select'}))
    gewicht = forms.IntegerField(label="Gewicht", min_value=500, widget=forms.NumberInput(
                                      attrs={'class': 'w3-input w3-border w3-light-grey'}))

    gekruid = forms.BooleanField(label="Gekruid", required=False, widget=forms.CheckboxInput(
        attrs={'class': 'w3-checkbox w3-input'}))
    bijz = temp_bijz
    prod_type = temp_prod_type
