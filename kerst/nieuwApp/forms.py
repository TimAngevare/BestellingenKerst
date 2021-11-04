from django.core.validators import RegexValidator
snijd_validator = RegexValidator(r"(\d+:\d+,)+", "x aantal keer: (gewicht):(aantal),")

from django import forms

TYPE_OPTION = (
    ("snijdvlees", "Snijdbaar vlees"),
    ("menu", "Menu"),
    ("gourmet", "Gourmet"),
    ("formaat", "Bepaald formaat"),
    ("bronvlees", "Speciaalvlees"),
    ("standaard", "Standaard"),
)

FORMAAT_OPTION = (
    ('klein', 'Klein'),
    ('groot', 'Groot'),
)

temp_product = forms.CharField(label="Product", max_length=100, widget=forms.TextInput(attrs={'class': 'w3-input w3-border w3-light-grey', 'list': 'products'}))
temp_cat = forms.CharField(label="Categorie", max_length=100, widget=forms.TextInput(attrs={'class': 'w3-input w3-border w3-light-grey'}))
temp_bijz = forms.CharField(label="Bijzonderheden", max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'w3-input w3-border w3-light-grey'}))
temp_prod_type = forms.ChoiceField(label="Type product", choices=TYPE_OPTION, widget=forms.Select(attrs={'class': 'w3-select'}))
temp_aantal = forms.IntegerField(label="Aantal", min_value=1, widget=forms.NumberInput(attrs={'class': 'w3-input w3-border w3-light-grey'}))
temp_gewicht = forms.IntegerField(label="Gewicht", min_value=0, widget=forms.NumberInput(attrs={'class': 'w3-input w3-border w3-light-grey'}))

class NieuweBestellingForm(forms.Form):
    prod_type = temp_prod_type
    usr_email = forms.EmailField(label="E-mail adres", max_length=100, widget=forms.EmailInput(attrs={'class': 'w3-input w3-border w3-light-grey'}))

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