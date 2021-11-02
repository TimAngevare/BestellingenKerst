from django.shortcuts import render
from django.http import HttpResponse

import datetime
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

        email = request.POST['usr_email']

        doc = {
            "email": email,
            "bestelnr": bestelnr,
            "producten": []
        }
        bests.insert_one(doc)

        return render(request, 'gekozenNieuw.html', {
            'gekozen_type': gekozen_type,
            'type_list': TYPES,
            'passed_bestelnr': bestelnr,
            'passed_email': email
        })

def nieuw_entry(request, bestelnr, email):
    try:
        gekozen_type = request.POST['prod_type']
    except (KeyError):
        return render(request, 'gekozenNieuw.html', {
            'error_message': "Je hebt geen type gekozen.",
            'gekozen_type': 'snijdbaar',
            'type_list': TYPES,
            'passed_bestelnr': bestelnr,
            'passed_email': email
        })
    else:
        return render(request, 'gekozenNieuw.html', {
            'gekozen_type': gekozen_type,
            'type_list': TYPES,
            'passed_bestelnr': bestelnr,
            'passed_email': email
        })

def bestel_done(request):
    bests.update_one({'bestelnr': int(request.POST['bestelnr'])},{"$set": {"email" : request.POST['usr_email'], "naam" : request.POST['naam'], "telnr" : request.POST['telnr'], "dagophalen" : request.POST['dagophalen'], "besteltijd" : datetime.datetime.utcnow()}})

    return render(request, 'nieuw.html', {
        'type_list': TYPES
    })

def bestel_pre_finish(request, bestelnr, email):
    
    return render(request, 'bestellingAfmaken.html', {
        'passed_bestelnr': bestelnr,
        'passed_email': email
    })

def nieuw_keuze(request):
    bestelnr = int(request.POST.get('bestelnr', '00000'))
    email = request.POST.get('usr_email', 'kkzooihetisfoutgegaan')

    #oude_type = request.POST['huidig_type']
    #if oude_type == 'snijdbaar':
    bestelling = Snijdvlees(request.POST['product'], request.POST['cat'], int(request.POST['gewicht']), request.POST['snijden'], request.POST['bijz'])
    
    bestelling.insert(int(bestelnr))

    if request.POST['done'] == 'Klaar':
        return(bestel_pre_finish(request, bestelnr, email))
    else:
        return(nieuw_entry(request, bestelnr, email))

def zoek(request):
    return HttpResponse("Hier kan je zoeken naar een bestelling.")