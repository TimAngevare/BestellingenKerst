from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.http import HttpResponse

import datetime
from random import choice

from .models import Snijdvlees, Menu, Gourmet, Formaat, BronVlees, Standaard
from .forms import NieuweBestellingForm, SnijdForm, GourmetForm, MenuForm, FormaatForm, BronVleesForm, StandaardForm

from utils import get_db
kerst_db = get_db('kerst_db')
bests = kerst_db['bestellingen']

prod_list = ['kip', 'ossenhaas', 'hamburger menu']

def index(request):
    return render(request, 'main.html', {
        "mainpage": True
    })

def nieuw(request):
    return render(request, 'nieuwApp/nieuw.html', {
        'form': NieuweBestellingForm()
    })

def kies_form(het_type):
    if het_type == 'snijdvlees':
        return SnijdForm()
    elif het_type == 'menu':
        return MenuForm()
    elif het_type == 'gourmet':
        return GourmetForm()
    elif het_type == 'formaat':
        return FormaatForm()
    elif het_type == 'bronvlees':
        return BronVleesForm()
    elif het_type == 'standaard':
        return StandaardForm()

def nieuw_bestel(request):
    if request.method == 'POST':
        form = NieuweBestellingForm(request.POST)
        if form.is_valid():

            """
            bestelnrlist = []
            for entry in bests.find():
                bestelnrlist.append(entry['bestelnr'])
            bestelnr = choice([i for i in range(1, 4001) if i not in bestelnrlist])
            """
            huidig_aantal_bests = bests.count()
            bestelnr = huidig_aantal_bests + 1

            email = form.cleaned_data['usr_email']
            gekozen_type = form.cleaned_data['prod_type']
            print(gekozen_type)

            doc = {
                "email": email,
                "bestelnr": bestelnr,
                "producten": []
            }
            bests.insert_one(doc)

            return render(request, 'nieuwApp/gekozenNieuw.html', {
                'gekozen_type': gekozen_type,
                'passed_bestelnr': bestelnr,
                'passed_email': email,
                'products_list': prod_list,
                'form': kies_form(gekozen_type)
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
            'error_message': "Je hebt geen type gekozen. Je hebt automatisch het formulier voor snijdbaar vlees gekregen.",
            'gekozen_type': 'snijdvlees',
            'passed_bestelnr': bestelnr,
            'passed_email': email,
            'products_list': prod_list,
            'form': SnijdForm()
        })
    else:
        return render(request, 'nieuwApp/gekozenNieuw.html', {
            'gekozen_type': gekozen_type,
            'passed_bestelnr': bestelnr,
            'passed_email': email,
            'products_list': prod_list,
            'form': kies_form(gekozen_type)
        })

def bestel_done(request):
    obj_bestelnrs = bests.find({}, {'bestelnr':1})
    list_bestelnrs = []
    for obj_bnr in obj_bestelnrs:
        list_bestelnrs.append(obj_bnr['bestelnr'])
    
    print(list_bestelnrs)
    dag_ophalen = request.POST['dagophalen']

    hoogst_huidig = 0

    for bnr in list_bestelnrs:
        string_bnr = str(bnr)
        if string_bnr[:2] == dag_ophalen[:2]:
            int_bnr = int(string_bnr[2:])
            if int_bnr > hoogst_huidig:
                hoogst_huidig = int_bnr
    
    nieuw_nr = hoogst_huidig + 1
    str_nieuw_nr = str(nieuw_nr)
    while len(str_nieuw_nr) < 4:
        str_nieuw_nr = '0' + str_nieuw_nr

    str_nieuw_bestelnr = dag_ophalen[:2] + str_nieuw_nr
    nieuw_bestelnr = int(str_nieuw_bestelnr)

    bests.update_one({'bestelnr': int(request.POST['bestelnr'])},{"$set": {"bestelnr": nieuw_bestelnr, "email" : request.POST['usr_email'], "naam" : request.POST['naam'], "telnr" : request.POST['telnr'], "dagophalen" : dag_ophalen, "besteltijd" : datetime.datetime.utcnow()}})

    return HttpResponseRedirect('/')

def bestel_pre_finish(request, bestelnr, email):
    
    return render(request, 'nieuwApp/bestellingAfmaken.html', {
        'passed_bestelnr': bestelnr,
        'passed_email': email
    })

def verwijder_best():
    print('nu verwijder ik de bestelling')

def nieuw_keuze(request):
    if request.method == 'POST':
        if request.POST['done'] == 'Verwijder bestelling':
            verwijder_best()
            return HttpResponseRedirect('/')
        
        bestelnr = request.POST['bestelnr']
        email = request.POST['usr_email']
        oude_type = request.POST['huidig_type']

        if oude_type == 'snijdvlees':
            form = SnijdForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                snijd_string = data['snijden']
                snijd_komma_splits = snijd_string.split(',')
                del snijd_komma_splits[-1]
                
                snijd_obj = {}

                for snijdoptie in snijd_komma_splits:
                    snijdvalue = snijdoptie.split(':')
                    snijd_obj[snijdvalue[0]] = int(snijdvalue[1])
                
                Snijdvlees(data['product'], data['cat'], int(data['gewicht']), snijd_obj, data['bijz']).insert(int(bestelnr))
            else:
                return render(request, 'nieuwApp/gekozenNieuw.html', {
                    'error_message': 'Je hebt snijden niet correct ingevoerd. De correcte manier is zovaak als je wil: (gewicht):(aantal),',
                    'gekozen_type': oude_type,
                    'passed_bestelnr': bestelnr,
                    'passed_email': email,
                    'products_list': prod_list,
                    'form': SnijdForm()
                })
        
        elif oude_type == 'menu':
            Menu(request.POST['product'], request.POST['cat'], int(request.POST['aantal']), request.POST['voorgerecht'], request.POST['hoofdgerecht'], request.POST['dessert'], request.POST['bijz']).insert(int(bestelnr))
        
        elif oude_type == 'gourmet':
            form = GourmetForm(request.POST)
            data = form.cleaned_data
            Gourmet(data['product'], data['cat'], data['conf'], data['bijz']).insert(int(bestelnr))
        
        elif oude_type == 'formaat':
            form = FormaatForm(request.POST)
            data = form.cleaned_data
            Formaat(data['product'], data['cat'], data['formaat'], data['aantal'], data['bijz']).insert(int(bestelnr))
        
        elif oude_type == 'bron':
            form = BronVleesForm(request.POST)
            data = form.cleaned_data
            BronVlees(data['product'], data['cat'], data['bron'], data['aantal'], data['bijz']).insert(int(bestelnr))
        
        elif oude_type == 'standaard':
            form = StandaardForm(request.POST)
            data = form.cleaned_data
            Standaard(data['product'], data['cat'], data['aantal'], data['bijz']).insert(int(bestelnr))
        

        if request.POST['done'] == 'Klaar':
            return(bestel_pre_finish(request, bestelnr, email))
        else:
            return(nieuw_entry(request, bestelnr, email))

    else:
        return HttpResponse("kk djalla dit moet niet kunnen ga naar home ofzo")