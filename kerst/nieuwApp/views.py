from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.http import HttpResponse

import datetime
from random import choice

from .models import Snijdvlees, Menu, Gourmet, Formaat, BronVlees, Standaard
from .forms import NieuweBestellingForm

from utils import get_db
kerst_db = get_db('kerst_db')
bests = kerst_db['bestellingen']

TYPES = {
    "snijdvlees": "Snijdbaar vlees",
    "menu": "Menu",
    "gourmet": "Gourmet",
    "formaat": "Bepaald formaat",
    "bronvlees": "Speciaalvlees",
    "standaard": "Standaard",
}
prod_list = ['kip', 'ossenhaas', 'hamburger menu']

def index(request):
    return render(request, 'main.html')

def nieuw(request):
    return render(request, 'nieuwApp/nieuw.html', {
        'form': NieuweBestellingForm()
    })


def nieuw_bestel(request):
    if request.method == 'POST':
        form = NieuweBestellingForm(request.POST)
        if form.is_valid():

            bestelnrlist = []
            for entry in bests.find():
                bestelnrlist.append(entry['bestelnr'])
            bestelnr = choice([i for i in range(1, 4001) if i not in bestelnrlist])

            email = form.cleaned_data['usr_email']
            gekozen_type = form.cleaned_data['prod_type']

            doc = {
                "email": email,
                "bestelnr": bestelnr,
                "producten": []
            }
            bests.insert_one(doc)

            return render(request, 'nieuwApp/gekozenNieuw.html', {
                'gekozen_type': gekozen_type,
                'type_dict': TYPES,
                'passed_bestelnr': bestelnr,
                'passed_email': email,
                'products_list': prod_list
            })
        
        return render(request, 'nieuwApp/nieuw.html', {
            'form': form
        })
    else:
        return HttpResponse("Wejow gek dit kan niet zomaar he.")

def nieuw_entry(request, bestelnr, email):
    try:
        gekozen_type = request.POST['prod_type']
    except (KeyError):
        return render(request, 'nieuwApp/gekozenNieuw.html', {
            'error_message': "Je hebt geen type gekozen.",
            'gekozen_type': 'snijdvlees',
            'type_dict': TYPES,
            'passed_bestelnr': bestelnr,
            'passed_email': email,
            'products_list': prod_list
        })
    else:
        return render(request, 'nieuwApp/gekozenNieuw.html', {
            'gekozen_type': gekozen_type,
            'type_dict': TYPES,
            'passed_bestelnr': bestelnr,
            'passed_email': email,
            'products_list': prod_list
        })

def bestel_done(request):
    bests.update_one({'bestelnr': int(request.POST['bestelnr'])},{"$set": {"email" : request.POST['usr_email'], "naam" : request.POST['naam'], "telnr" : request.POST['telnr'], "dagophalen" : request.POST['dagophalen'], "besteltijd" : datetime.datetime.utcnow()}})

    return HttpResponseRedirect('/')

def bestel_pre_finish(request, bestelnr, email):
    
    return render(request, 'nieuwApp/bestellingAfmaken.html', {
        'passed_bestelnr': bestelnr,
        'passed_email': email
    })

def nieuw_keuze(request):
    bestelnr = request.POST['bestelnr']
    email = request.POST['usr_email']

    oude_type = request.POST['huidig_type']
    if oude_type == 'snijdvlees':
        snijd_string = request.POST['snijden']
        snijd_komma_splits = snijd_string.split(',')
        del snijd_komma_splits[-1]
        
        snijd_obj = {}

        for snijdoptie in snijd_komma_splits:
            snijdvalue = snijdoptie.split(':')
            snijd_obj[snijdvalue[0]] = int(snijdvalue[1])
        
        Snijdvlees(request.POST['product'], request.POST['cat'], int(request.POST['gewicht']), snijd_obj, request.POST['bijz']).insert(int(bestelnr))
    
    elif oude_type == 'menu':
        Menu(request.POST['product'], request.POST['cat'], int(request.POST['aantal']), request.POST['voorgerecht'], request.POST['hoofdgerecht'], request.POST['dessert'], request.POST['bijz']).insert(int(bestelnr))
    
    elif oude_type == 'gourmet':
        Gourmet(request.POST['product'], request.POST['cat'], request.POST['conf']).insert(int(bestelnr))
    
    elif oude_type == 'formaat':
        Formaat(request.POST['product'], request.POST['cat'], request.POST['formaat']).insert(int(bestelnr))
    
    elif oude_type == 'bron':
        BronVlees(request.POST['product'], request.POST['cat'], request.POST['bron'], request.POST['aantal']).insert(int(bestelnr))
    
    elif oude_type == 'standaard':
        Standaard(request.POST['product'], request.POST['cat'], request.POST['aantal']).insert(int(bestelnr))
    
    if request.POST['done'] == 'Klaar':
        return(bestel_pre_finish(request, bestelnr, email))
    else:
        return(nieuw_entry(request, bestelnr, email))