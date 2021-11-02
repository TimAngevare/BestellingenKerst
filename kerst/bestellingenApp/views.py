from django.shortcuts import render
from django.http import HttpResponse

from random import choice
from .models import Snijdvlees

TYPES = ['snijdvlees', 'menu', 'gourmet','formaat', 'bronvlees']

from utils import get_db
kerst_db = get_db('kerst_db')
bests = kerst_db['bestellingen']

def index(request):
    return render(request, 'main.html')

def nieuw(request):
    return render(request, 'nieuw.html', {
        'type_list': TYPES
    })


def nieuw_bestel(request):
    try:
        gekozen_type = request.POST['prod_type']
    except (KeyError):
        return render(request, 'nieuw.html', {
            'error_message': "Je hebt geen type gekozen.",
            'type_list': TYPES
        })
    else:

        bestelnrlist = []
        for entry in bests.find():
            bestelnrlist.append(entry['bestelnr'])
        bestelnr = choice([i for i in range(1, 4001) if i not in bestelnrlist])

        doc = {
            "email": request.POST['email'],
            "bestelnr": bestelnr,
            "producten": []
        }
        bests.insert_one(doc)

        return render(request, 'gekozenNieuw.html', {
            'gekozen_type': gekozen_type,
            'type_list': TYPES,
            'bestelnr': bestelnr
        })

def nieuw_entry(request):
    bestelnr = int(request.POST['bestelnr'])
    
    #oude_type = request.POST['huidig_type']
    #if oude_type == 'snijdbaar':
    bestelling = Snijdvlees(request.POST['product'], request.POST['cat'], int(request.POST['gewicht']), request.POST['snijden'], request.POST['bijz'])
    
    bestelling.insert(int(bestelnr))

    try:
        gekozen_type = request.POST['prod_type']
    except (KeyError):
        return render(request, 'gekozenNieuw.html', {
            'error_message': "Je hebt geen type gekozen.",
            'gekozen_type': 'snijdbaar',
            'type_list': TYPES,
            'bestelnr': bestelnr
        })
    else:
        return render(request, 'gekozenNieuw.html', {
            'gekozen_type': gekozen_type,
            'type_list': TYPES,
            'bestelnr': bestelnr
        })

def bestel_finish(request):
    return HttpResponse('Je bent klaar.')

def nieuw_keuze(request):
    if request.POST['done'] == 'Klaar':
        return(bestel_finish(request))
    else:
        return(nieuw_entry(request))

def zoek(request):
    return HttpResponse("Hier kan je zoeken naar een bestelling.")