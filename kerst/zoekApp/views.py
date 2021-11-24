from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from . import forms
import mongo_manage

def zoek(request):
    return render(request, 'zoekApp/zoek.html')


def bestellingen(request):
    if request.method == "POST":
        bestel_form = forms.bestellingen(request.POST)
        if bestel_form.is_valid():
            num = bestel_form.cleaned_data["bestel_nmr"]
            tel = bestel_form.cleaned_data["tel"]
            dag = bestel_form.cleaned_data["dag_ophalen"]
            resultaten = mongo_manage.zoek_best(num, tel, dag)
            totaal = resultaten.count()
            return render(request, 'zoekApp/bestellingen_results.html', {"resultaten": resultaten, "totaal" : totaal}) 
        else:
            messages.error(request, "Hier klopt iets niet, vul opnieuw in")
        #return HttpResponse("zoekApp/bestellingen_results.html") 
    else:
        bestel_form = forms.bestellingen()
    return render(request, 'zoekApp/bestellingen.html', {"bestel_form": bestel_form})


#def bestellingen_resultaten(request):
    #return render(request, 'zoekApp/bestellingen_results.html', {"resultaten": resultaten})


def producten(request):
    if request.method == "POST":
        producten_form = forms.producten(request.POST)
        if producten_form.is_valid():
            typ_prod = producten_form.cleaned_data["temp_prod_type"]
            prod = producten_form.cleaned_data["temp_product"]
            resultaten = mongo_manage.zoek_prod(typ_prod, prod)
            totaal = resultaten.count()
            return render(request, 'zoekApp/producten_results.html', {"resultaten": resultaten, "totaal" : totaal}) 
        else:
            messages.error(request, "Hier klopt iets niet, vul opnieuw in")
        #return HttpResponse("zoekApp/bestellingen_results.html") 
    else:
        producten_form = forms.producten()
    return render(request, 'zoekApp/producten.html', {"producten_form": producten_form})


def alles(request):
    if request.method == "POST":
        alles_form = forms.alles(request.POST)
        if alles_form.is_valid():
            dag = alles_form.cleaned_data["dag"]
            state = alles_form.cleaned_data["state"]
            resultaten = mongo_manage.zoek_best_alles(dag, state)
            totaal = resultaten.count()
            return render(request, 'zoekApp/alles.html', {"resultaten": resultaten, "totaal" : totaal}) 
        else:
            messages.error(request, "Hier klopt iets niet, vul opnieuw in")
        #return HttpResponse("zoekApp/bestellingen_results.html") 
    else:
        alles_form = forms.alles()
    return render(request, 'zoekApp/alles.html', {"alles_form": alles_form})
