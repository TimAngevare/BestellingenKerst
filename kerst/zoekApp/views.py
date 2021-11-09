from django.shortcuts import render
from . import forms

def zoek(request):
    bestel_form = forms.Bestellingen()
    return render(request, 'zoekApp/zoek.html', {"bestel_form":bestel_form})

def bestellingen(request):
    pass

def producten(request):
    pass

def alles(request):
    pass

