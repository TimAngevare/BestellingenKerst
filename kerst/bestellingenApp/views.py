from django.shortcuts import render
from django.http import HttpResponse

TYPES = ['snijdvlees', 'menu', 'gourmet','formaat', 'bronvlees']

from utils import get_db
kerst_db = get_db('kerst_db')
best = kerst_db['bestellingen']

def index(request):
    return render(request, 'main.html')

def nieuw(request):
    return render(request, 'nieuw.html', {
        'type_list': TYPES
    })


def nieuwType(request):
    if request.POST['done'] == 'Kies' or request.POST['done'] == 'Nog een product':
        try:
            gekozen_type = request.POST['prod_type']
        except (KeyError):
            return render(request, 'nieuw.html', {
                'error_message': "Je hebt geen type gekozen.",
                'type_list': TYPES
            })
        else:
            return render(request, 'gekozenNieuw.html', {
                'gekozen_type': gekozen_type,
                'type_list': TYPES
            })
    else:
        return HttpResponse('je was klaar')

def zoek(request):
    return HttpResponse("Hier kan je zoeken naar een bestelling.")