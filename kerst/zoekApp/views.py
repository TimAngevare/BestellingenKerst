from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from . import forms
import mongo_manage

from nieuwApp.views import alle_prodlist

PROD = alle_prodlist


def zoek(request):
    return render(request, 'zoekApp/zoek.html')


def bestellingen(request):
    if request.method == "POST":
        bestel_form = forms.bestellingen(request.POST)
        for key in request.POST.keys():
            if key.startswith('voltooi-'):
                prod = key[8:]
                mongo_manage.update_state_best(prod, 'voltooid')
                return render(request, 'zoekApp/bestellingen.html', {"bestel_form": bestel_form})
            elif key.startswith('probleem-'):
                prod = key[9:]
                mongo_manage.update_state_best(prod, 'probleem')
                return render(request, 'zoekApp/bestellingen.html', {"bestel_form": bestel_form})
            elif key.startswith('behandeling-'):
                prod = key[12:]
                mongo_manage.update_state_best(prod, 'bezig')
                return render(request, 'zoekApp/bestellingen.html', {"bestel_form": bestel_form})
        if bestel_form.is_valid():
            num = bestel_form.cleaned_data["bestel_nmr"]
            tel = bestel_form.cleaned_data["tel"]
            dag = bestel_form.cleaned_data["dag_ophalen"]
            naam = bestel_form.cleaned_data["naam"]
            resultaten = mongo_manage.zoek_best({'bestelnr': num, 'telnr': tel, 'dagophalen': dag, 'naam': naam})
            totaal = resultaten[0]
            return render(request, 'zoekApp/bestellingen_results.html', {"resultaten": resultaten[1], "totaal": totaal})
        else:
            messages.error(request, "Hier klopt iets niet, vul opnieuw in")
        # return HttpResponse("zoekApp/bestellingen_results.html")
    else:
        bestel_form = forms.bestellingen()
    return render(request, 'zoekApp/bestellingen.html', {"bestel_form": bestel_form})


# def bestellingen_resultaten(request):
# return render(request, 'zoekApp/bestellingen_results.html', {"resultaten": resultaten})


def producten(request):
    if request.method == "POST":
        producten_form = forms.producten(request.POST)
        for key in request.POST.keys():
            if key.startswith('voltooi-'):
                prod = key[8:]
                mongo_manage.update_state_prod(prod, 'voltooid')
                return render(request, 'zoekApp/producten.html',
                              {"producten_form": producten_form, "products_list": PROD})
            elif key.startswith('probleem-'):
                prod = key[9:]
                mongo_manage.update_state_prod(prod, 'probleem')
                return render(request, 'zoekApp/producten.html',
                              {"producten_form": producten_form, "products_list": PROD})
            elif key.startswith('behandeling-'):
                prod = key[12:]
                mongo_manage.update_state_prod(prod, 'bezig')
                return render(request, 'zoekApp/producten.html',
                              {"producten_form": producten_form, "products_list": PROD})
        if producten_form.is_valid():
            typ_prod = producten_form.cleaned_data["temp_prod_type"]
            prod = producten_form.cleaned_data["temp_product"]
            state = producten_form.cleaned_data["state"]
            resultaten = mongo_manage.zoek_prod({'cat': typ_prod, 'product': prod, 'state': state})
            totaal = resultaten[0]
            return render(request, 'zoekApp/producten_results.html', {"resultaten": resultaten[1], "totaal": totaal})
        else:
            messages.error(request, "Hier klopt iets niet, vul opnieuw in")
        # return HttpResponse("zoekApp/bestellingen_results.html")
    else:
        producten_form = forms.producten()
    return render(request, 'zoekApp/producten.html', {"producten_form": producten_form, "products_list": PROD})


def alles(request):
    if request.method == "POST":
        alles_form = forms.alles(request.POST)
        if alles_form.is_valid():
            dag = alles_form.cleaned_data["dag"]
            state = alles_form.cleaned_data["state"]
            return redirect('/zoek/alles?dag=' + dag + "&state=" + state + "&nmr=")
        else:
            messages.error(request, "Hier klopt iets niet, vul opnieuw in")
        # return HttpResponse("zoekApp/bestellingen_results.html")
    else:
        alles_form = forms.alles()
    return render(request, 'zoekApp/alles.html', {"alles_form": alles_form})


def alles_result(request):
    dag = request.GET['dag']
    state = request.GET['state']
    nmr = request.GET['nmr']
    if request.method == "POST":
        for key in request.POST.keys():
            if key.startswith('voltooi-'):
                bestel_nmr = key[8:]
                mongo_manage.update_state_best(int(bestel_nmr), 'voltooid')
            elif key.startswith('probleem-'):
                bestel_nmr = key[9:]
                mongo_manage.update_state_best(int(bestel_nmr), 'probleem')
            elif key.startswith('behandeling-'):
                bestel_nmr = key[12:]
                print("hola " + bestel_nmr)
                mongo_manage.update_state_best(int(bestel_nmr), 'bezig')
                return redirect('/zoek/alles?dag=&state=bezig&nmr=' + bestel_nmr)
    resultaten = mongo_manage.zoek_best_alles({'dagophalen': dag, 'state': state})
    totaal = resultaten[0]
    return render(request, 'zoekApp/alles_results.html', {"resultaten": resultaten[1], "totaal": totaal})
