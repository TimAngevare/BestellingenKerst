from django.core.validators import RegexValidator
snijd_validator = RegexValidator(r"(\d+:\d+,)+", "x aantal keer: (gewicht):(aantal),")
telnr_validator = RegexValidator(r"^\+316\d{8}$", "Moet beginnen met: +316")

from django import forms

TYPE_OPTION = (
    ("standaard", "Standaard"),
    ("snijdvlees", "Snijdbaar vlees"),
    ("menu", "Menu"),
    ("gourmet", "Gourmet"),
    ("formaat", "Bepaald formaat"),
    ("bronvlees", "Speciaalvlees"),
)

FORMAAT_OPTION = (
    ('klein', 'Klein'),
    ('groot', 'Groot'),
)

DAGEN_OPHALEN_OPTION = [
    ('23', '23-12'),
    ('24', '24-12'),
    ('25', '25-12')
]

temp_product = forms.CharField(label="Product", max_length=100, widget=forms.TextInput(attrs={'class': 'w3-input w3-border w3-light-grey', 'list': 'products'}))
temp_cat = forms.CharField(label="Categorie", max_length=100, widget=forms.TextInput(attrs={'class': 'w3-input w3-border w3-light-grey'}))
temp_bijz = forms.CharField(label="Bijzonderheden", max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'w3-input w3-border w3-light-grey'}))
temp_prod_type = forms.ChoiceField(label="Type product", choices=TYPE_OPTION, widget=forms.Select(attrs={'class': 'w3-select'}))
temp_aantal = forms.IntegerField(label="Aantal", min_value=1, widget=forms.NumberInput(attrs={'class': 'w3-input w3-border w3-light-grey'}))
temp_gewicht = forms.IntegerField(label="Gewicht", min_value=0, widget=forms.NumberInput(attrs={'class': 'w3-input w3-border w3-light-grey'}))

class NieuweBestellingForm(forms.Form):
    prod_type = temp_prod_type
    usr_email = forms.EmailField(label="E-mail adres", max_length=100, widget=forms.EmailInput(attrs={'class': 'w3-input w3-border w3-light-grey'}))

class BestellingAfmakenForm(forms.Form):
    naam = forms.CharField(label="Naam", max_length=150, widget=forms.TextInput(attrs={'class': 'w3-input w3-border w3-light-grey'}))
    telnr = forms.CharField(label="Telefoon nummer", max_length=12, validators=[telnr_validator], widget=forms.TextInput(attrs={'class': 'w3-input w3-border w3-light-grey', 'value': '+316'}))
    dagophalen = forms.ChoiceField(label="Dag ophalen", choices=DAGEN_OPHALEN_OPTION, widget=forms.RadioSelect())

class SnijdForm(forms.Form):
    product = temp_product
    cat = temp_cat
    gewicht = temp_gewicht
    snijden = forms.CharField(label="Snijden", max_length=100, validators=[snijd_validator], widget=forms.TextInput(attrs={'class': 'w3-input w3-border w3-light-grey'}))
    
    bijz = temp_bijz
    prod_type = temp_prod_type

class MenuForm(forms.Form):
    product = temp_product
    cat = temp_cat
    aantal = temp_aantal

    carpaccio = forms.IntegerField(label="(V-gerecht) Carpaccio", min_value=0, widget=forms.NumberInput(attrs={'class': 'w3-input w3-border w3-light-grey', 'value': '0'}))
    vitello_tonato = forms.IntegerField(label="(V-gerecht) Vitello tonato", min_value=0, widget=forms.NumberInput(attrs={'class': 'w3-input w3-border w3-light-grey', 'value': '0'}))
    kalfsragout = forms.IntegerField(label="(V-gerecht) Kalfsragout", min_value=0, widget=forms.NumberInput(attrs={'class': 'w3-input w3-border w3-light-grey', 'value': '0'}))
    biefstuk = forms.IntegerField(label="(H-gerecht) Biefstuk", min_value=0, widget=forms.NumberInput(attrs={'class': 'w3-input w3-border w3-light-grey', 'value': '0'}))
    varkenshaas = forms.IntegerField(label="(H-gerecht) Varkenshaas", min_value=0, widget=forms.NumberInput(attrs={'class': 'w3-input w3-border w3-light-grey', 'value': '0'}))
    tiramisu = forms.IntegerField(label="(Dessert) Tiramisu", min_value=0, widget=forms.NumberInput(attrs={'class': 'w3-input w3-border w3-light-grey', 'value': '0'}))
    apfelstrudel = forms.IntegerField(label="(Dessert) Apfelstrudel", min_value=0, widget=forms.NumberInput(attrs={'class': 'w3-input w3-border w3-light-grey', 'value': '0'}))

    bijz = temp_bijz
    prod_type = temp_prod_type

class GourmetForm(forms.Form):
    product = temp_product
    cat = temp_cat
    
    bijz = temp_bijz
    prod_type = temp_prod_type

class FormaatForm(forms.Form):
    product = temp_product
    cat = temp_cat
    formaat = forms.ChoiceField(label="Formaat", choices=FORMAAT_OPTION, widget=forms.Select(attrs={'class': 'w3-select'}))
    aantal = temp_aantal
    
    bijz = temp_bijz
    prod_type = temp_prod_type

class BronVleesForm(forms.Form):
    product = temp_product
    cat = temp_cat
    bron = forms.CharField(label="Bron", max_length=100, widget=forms.TextInput(attrs={'class': 'w3-input w3-border w3-light-grey'}))
    gewicht = temp_gewicht
    
    bijz = temp_bijz
    prod_type = temp_prod_type

class StandaardForm(forms.Form):
    product = temp_product
    cat = temp_cat
    aantal = temp_aantal
    
    bijz = temp_bijz
    prod_type = temp_prod_type