from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages

import datetime

from .models import *
from .forms import *

from utils import get_db

kerst_db = get_db('kerst_db')
bests = kerst_db['bestellingen']
prods = kerst_db['producten']

obj_prods = prods.find({}, {'product': 1})
prod_list = []
for obj_prod in obj_prods:
    prod_list.append(obj_prod['product'])


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
        return SnijdForm(), prod_list
    elif het_type == 'menu':
        return MenuForm(), prod_list
    elif het_type == 'gourmet':
        return GourmetForm(), prod_list
    # elif het_type == 'formaat':
    #     return FormaatForm(), prod_list
    elif het_type == 'dryaged':
        return DryAgedForm(), prod_list
    elif het_type == 'standaard':
        return StandaardForm(), prod_list


def nieuw_bestel(request):
    if request.method == 'POST':
        form = NieuweBestellingForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['usr_email'].strip()
            gekozen_type = form.cleaned_data['prod_type']
            dag_ophalen = form.cleaned_data['dagophalen']

            obj_bestelnrs = bests.find({}, {'bestelnr': 1})
            list_bestelnrs = []
            for obj_bnr in obj_bestelnrs:
                list_bestelnrs.append(obj_bnr['bestelnr'])

            hoogst_huidig = 0

            for bnr in list_bestelnrs:
                string_bnr = str(bnr)
                if string_bnr[:2] == dag_ophalen:
                    int_bnr = int(string_bnr[2:])
                    if int_bnr > hoogst_huidig:
                        hoogst_huidig = int_bnr

            nieuw_nr = hoogst_huidig + 1
            str_nieuw_nr = str(nieuw_nr)
            while len(str_nieuw_nr) < 4:
                str_nieuw_nr = '0' + str_nieuw_nr

            str_nieuw_bestelnr = dag_ophalen + str_nieuw_nr
            nieuw_bestelnr = int(str_nieuw_bestelnr)

            doc = {
                "email": email,
                "bestelnr": nieuw_bestelnr,
                "producten": []
            }
            bests.insert_one(doc)

            form_info = kies_form(gekozen_type)
            return render(request, 'nieuwApp/gekozenNieuw.html', {
                'gekozen_type': gekozen_type,
                'passed_bestelnr': nieuw_bestelnr,
                'passed_email': email,
                'products_list': prod_list,
                'form': form_info[0]
            })
        else:
            messages.error(request, "niet alles ingevuld")
        return render(request, 'nieuwApp/nieuw.html', {
            'form': form
        })
    else:
        return HttpResponse("Wejow gek dit kan niet zomaar he.")


def bestel_done(request):
    if request.method == 'POST':
        bestelnr = request.POST['bestelnr']
        email = request.POST['usr_email']

        if request.POST['done'] == "Nog een product":
            prod_type = request.POST['prod_type']
            form_info = kies_form(prod_type)
            return render(request, 'nieuwApp/gekozenNieuw.html', {
                'gekozen_type': prod_type,
                'passed_bestelnr': bestelnr,
                'passed_email': email,
                'products_list': prod_list,
                'form': form_info[0]
            })

        form = BestellingAfmakenForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            bests.update_one({'bestelnr': int(bestelnr)}, {
                "$set": {"email": email,
                         "naam": data['naam'],
                         "telnr": data['telnr'],
                         "dagophalen": bestelnr[:2],
                         "tijdophalen": int(data['tijdophalen']),
                         "besteltijd": datetime.datetime.utcnow()
                         }
            })

            return HttpResponseRedirect('/')
        else:
            return render(request, 'nieuwApp/bestellingAfmaken.html', {
                'error_message': 'Oeps er is iets mis, waarschijnlijk heb je het telefoonnummer of de tijd van ophalen niet correct ingevoerd.',
                'passed_bestelnr': request.POST['bestelnr'],
                'passed_email': request.POST['usr_email'],
                'form': form
            })
    else:
        return HttpResponse("ja dit kan dus weer niet he")


def prod_toevoegen(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        bestelnr = int(request.POST['bestelnr'])
        email = request.POST['usr_email']
        oude_type = request.POST['huidig_type']
        nieuw_form = kies_form(oude_type)

        if request.POST['done'] == "Annuleren":
            return render(request, 'nieuwApp/gekozenNieuw.html', {
                'gekozen_type': oude_type,
                'passed_bestelnr': bestelnr,
                'passed_email': email,
                'products_list': prod_list,
                'form': nieuw_form[0]
            })
        elif form.is_valid():
            data = form.cleaned_data
            nieuw_prod = data['product'].strip()
            Product(nieuw_prod, data['cat']).insert()
            prod_list.append(nieuw_prod)

            return render(request, 'nieuwApp/gekozenNieuw.html', {
                'gekozen_type': oude_type,
                'passed_bestelnr': bestelnr,
                'passed_email': email,
                'products_list': prod_list,
                'form': nieuw_form[0]
            })
        else:
            return render(request, 'nieuwApp/nieuwProduct.html', {
                'error_message': 'Oeps, er klopt iets niet. Probeer het even opnieuw',
                'nieuw_prod': request.POST['product'],
                'gekozen_type': oude_type,
                'passed_bestelnr': bestelnr,
                'passed_email': email,
                'form': form
            })
    else:
        return HttpResponse("Gast dit kan niet jonge")


def nieuw_keuze(request):
    if request.method == 'POST':
        bestelnr = int(request.POST['bestelnr'])
        email = request.POST['usr_email']
        oude_type = request.POST['huidig_type']
        nieuw_type = request.POST['prod_type']

        if request.POST['done'] == 'Verwijder bestelling':
            bests.delete_one({'bestelnr': bestelnr})
            return HttpResponseRedirect('/')

        if request.POST['product'] not in prod_list:
            return render(request, 'nieuwApp/nieuwProduct.html', {
                'nieuw_prod': request.POST['product'],
                'gekozen_type': oude_type,
                'passed_bestelnr': bestelnr,
                'passed_email': email,
                'form': ProductForm()
            })

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

                Snijdvlees(data['product'], int(data['gewicht']), snijd_obj, data['bijz']).insert(bestelnr)
            else:
                return render(request, 'nieuwApp/gekozenNieuw.html', {
                    'error_message': 'Oeps er is iets mis, waarschijnlijk heb je snijden niet correct ingevoerd. De correcte manier is (zovaak als je wil): (gewicht):(aantal),',
                    'gekozen_type': oude_type,
                    'passed_bestelnr': bestelnr,
                    'passed_email': email,
                    'products_list': prod_list,
                    'form': SnijdForm()
                })

        elif oude_type == 'menu':
            form = MenuForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data

                if data['product'] == 'traditioneel_kerstmenu':
                    v_gerecht_doc = {}

                    int_carp = int(data['carpaccio'])
                    int_ragout = int(data['kalfsragout'])
                    if int_carp > 0:
                        v_gerecht_doc['carpaccio'] = int_carp
                    if int_ragout > 0:
                        v_gerecht_doc['kalfsragout'] = int_ragout

                    Menu('traditioneel_kerstmenu', int(data['aantal']), v_gerecht_doc, 'beef wellington',
                         'dessert buffet', data['bijz']).insert(bestelnr)
                else:
                    v_gerecht_doc = {}
                    h_gerecht_doc = {}
                    dessert_doc = {}

                    int_carp = int(data['carpaccio'])
                    int_vt = int(data['vitello_tonato'])
                    int_biefstuk = int(data['biefstuk'])
                    int_varkenshaas = int(data['varkenshaas'])
                    int_tiramisu = int(data['tiramisu'])
                    int_apfelstrudel = int(data['apfelstrudel'])

                    if int_carp > 0: v_gerecht_doc['carpaccio'] = int_carp
                    if int_vt > 0: v_gerecht_doc['vitello_tonato'] = int_vt
                    if int_biefstuk > 0: h_gerecht_doc['biefstuk'] = int_biefstuk
                    if int_varkenshaas > 0: h_gerecht_doc['varkenshaas'] = int_varkenshaas
                    if int_tiramisu > 0: dessert_doc['tiramisu'] = int_tiramisu
                    if int_apfelstrudel > 0: dessert_doc['apfelstrudel'] = int_apfelstrudel

                    Menu('dorpsslagers_kerstmenu', int(data['aantal']), v_gerecht_doc, h_gerecht_doc, dessert_doc,
                         data['bijz']).insert(bestelnr)

            else:
                return render(request, 'nieuwApp/gekozenNieuw.html', {
                    'error_message': 'Oeps, er is iets mis gegaan. Waarschijnlijk heb je niet een menu-product gekozen.',
                    'gekozen_type': oude_type,
                    'passed_bestelnr': bestelnr,
                    'passed_email': email,
                    'products_list': prod_list,
                    'form': form
                })

        elif oude_type == 'gourmet':
            form = GourmetForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                conf_doc = {}
                menu_items = ['bavette', 'kogel_biefstuk', 'ossenhaaspuntjes', 'ba_hamburgers', 'rundervink',
                              'speklapjes', 'varkenshaassate', 'shoarma', 'varkenshaas', 'kip_bacon_chili', 'slavink',
                              'kipfilet', 'hamburger', 'lamsrack', 'dry_aged', 'kalfsoester', 'diamanthaas',
                              'ba_cheddar', 'chipolata', 'chinese_roaststeak']

                for optie in menu_items:
                    int_optie = int(data[optie])
                    if int_optie > 0: conf_doc[optie] = int_optie

                Gourmet('custom_gourmet', conf_doc, data['bijz']).insert(bestelnr)
            else:
                return render(request, 'nieuwApp/gekozenNieuw.html', {
                    'error_message': 'Oeps, er is iets mis gegaan. Check je inputs en probeer het aub opnieuw.',
                    'gekozen_type': oude_type,
                    'passed_bestelnr': bestelnr,
                    'passed_email': email,
                    'products_list': prod_list,
                    'form': form
                })

        elif oude_type == 'dryaged':
            form = DryAgedForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                DryAgedVlees(data['product'], data['soort'], data['gewicht'], data['bijz']).insert(bestelnr)
            else:
                return render(request, 'nieuwApp/gekozenNieuw.html', {
                    'error_message': 'Oeps, er is iets mis gegaan. Check je inputs en probeer het aub opnieuw.',
                    'gekozen_type': oude_type,
                    'passed_bestelnr': bestelnr,
                    'passed_email': email,
                    'products_list': prod_list,
                    'form': form
                })

        elif oude_type == 'standaard':
            form = StandaardForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                Standaard(data['product'], data['aantal'], data['bijz']).insert(bestelnr)
            else:
                return render(request, 'nieuwApp/gekozenNieuw.html', {
                    'error_message': 'Oeps, er is iets mis gegaan. Check je inputs en probeer het aub opnieuw.',
                    'gekozen_type': oude_type,
                    'passed_bestelnr': bestelnr,
                    'passed_email': email,
                    'products_list': prod_list,
                    'form': form
                })

        if request.POST['done'] == 'Klaar':
            return render(request, 'nieuwApp/bestellingAfmaken.html', {
                'passed_bestelnr': bestelnr,
                'passed_email': email,
                'form': BestellingAfmakenForm()
            })
        else:
            form_info = kies_form(nieuw_type)
            return render(request, 'nieuwApp/gekozenNieuw.html', {
                'gekozen_type': nieuw_type,
                'passed_bestelnr': bestelnr,
                'passed_email': email,
                'products_list': prod_list,
                'form': form_info[0]
            })

    else:
        return HttpResponse(
            "sjongejonge dit is niet de bedoeling, hup ga weer terug naar home, toe maar, ga dan, komaan, tempo please")
