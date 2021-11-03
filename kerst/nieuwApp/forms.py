from django import forms

TYPE_OPTION = (
    ("snijdvlees", "Snijdbaar vlees"),
    ("menu", "Menu"),
    ("gourmet", "Gourmet"),
    ("formaat", "Bepaald formaat"),
    ("bronvlees", "Speciaalvlees"),
    ("standaard", "Standaard"),
)

class NieuweBestellingForm(forms.Form):
    prod_type = forms.ChoiceField(label="Type product", choices=TYPE_OPTION, widget=forms.Select(attrs={'class': 'w3-select'}))
    usr_email = forms.EmailField(label="E-mail adres", max_length=100, widget=forms.EmailInput(attrs={'class': 'w3-input w3-border w3-light-grey'}))