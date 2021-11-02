from django import forms

TYPE_OPTION = (
    ("snijdvlees", "Snijdbaar vlees"),
    ("menu", "Menu"),
    ("gourmet", "Gourmet"),
    ("formaat", "Bepaald formaat"),
    ("bronvlees", "Vlees uit..."),
    ("standaard", "Standaard"),
)

class NieuweBestellingForm(forms.Form):
    prod_type = forms.ChoiceField(label="Type product", choices=TYPE_OPTION)
    usr_email = forms.EmailField(label="E-mail adres", max_length=100)