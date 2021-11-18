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
            return render(request, 'zoekApp/bestellingen_results.html', {"resultaten": resultaten}) 
        else:
            num = "2301"
            messages.error(request, "Hier klopt iets niet, vul opnieuw in")
        #return HttpResponse("zoekApp/bestellingen_results.html") 
    else:
        bestel_form = forms.bestellingen()
    return render(request, 'zoekApp/bestellingen.html', {"bestel_form": bestel_form})


#def bestellingen_resultaten(request):
    #return render(request, 'zoekApp/bestellingen_results.html', {"resultaten": resultaten})


def producten(request):
    pass


def alles(request):
    pass
