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
        return SnijdForm()
    elif het_type == 'menu':
        return MenuForm()
    elif het_type == 'zelf_gourmet':
        return GourmetForm()
    elif het_type == 'dry_aged':
        return DryAgedForm()
    elif het_type == 'standaard':
        return StandaardForm()


def huidig_producten(bestelnr):
    producten = bests.find_one({'bestelnr': bestelnr}, {'producten': 1})
    return_string = ""
    if len(producten['producten']) > 0:
        for product in producten['producten']:
            try:
                return_string += product['product'] + " (x" + str(product['aantal']) + "), "
            except KeyError:
                try:
                    return_string += product['product'] + " (" + str(product['gewicht']) + " gr.), "
                except KeyError:
                    return_string += product['product'] + ", "
    else:
        return_string = "Nog geen producten toegevoegd"

    if return_string[-2:] == ", ":
        return return_string[:-2]

    return return_string


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
            while len(str_nieuw_nr) < 3:
                str_nieuw_nr = '0' + str_nieuw_nr

            str_nieuw_bestelnr = dag_ophalen + str_nieuw_nr
            nieuw_bestelnr = int(str_nieuw_bestelnr)

            doc = {
                "email": email,
                "bestelnr": nieuw_bestelnr,
                "producten": []
            }
            bests.insert_one(doc)

            return render(request, 'nieuwApp/gekozenNieuw.html', {
                'gekozen_type': gekozen_type,
                'passed_bestelnr': nieuw_bestelnr,
                'passed_email': email,
                'products_list': prod_list,
                'product_form': kies_form(gekozen_type),
                'speciale_optie_form': SpecialeOptieForm(),
                'huidige_producten': huidig_producten(nieuw_bestelnr)
            })
        else:
            messages.error(request, "niet alles ingevuld")
        return render(request, 'nieuwApp/nieuw.html', {
            'product_form': form,
            'speciale_optie_form': SpecialeOptieForm()
        })
    else:
        return HttpResponse("Wejow gek dit kan niet zomaar he.")


def bestel_done(request):
    if request.method == 'POST':
        bestelnr = request.POST['bestelnr']
        email = request.POST['usr_email']

        if request.POST['done'] == "Nog een product":
            prod_type = request.POST['prod_type']
            return render(request, 'nieuwApp/gekozenNieuw.html', {
                'gekozen_type': prod_type,
                'passed_bestelnr': bestelnr,
                'passed_email': email,
                'products_list': prod_list,
                'product_form': kies_form(prod_type),
                'speciale_optie_form': SpecialeOptieForm(),
                'huidige_producten': huidig_producten(bestelnr)
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
                'form': BestellingAfmakenForm(),
                'speciale_optie_form': SpecialeOptieForm(),
                'huidige_producten': huidig_producten(request.POST['bestelnr'])
            })
    else:
        return HttpResponse("ja dit kan dus weer niet he")


def prod_toevoegen(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        bestelnr = int(request.POST['bestelnr'])
        email = request.POST['usr_email']
        oude_type = request.POST['huidig_type']

        if request.POST['done'] == "Annuleren":
            return render(request, 'nieuwApp/gekozenNieuw.html', {
                'gekozen_type': oude_type,
                'passed_bestelnr': bestelnr,
                'passed_email': email,
                'products_list': prod_list,
                'product_form': kies_form(oude_type),
                'speciale_optie_form': SpecialeOptieForm(),
                'huidige_producten': huidig_producten(bestelnr)
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
                'product_form': kies_form(oude_type),
                'speciale_optie_form': SpecialeOptieForm(),
                'huidige_producten': huidig_producten(bestelnr)
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


def speciale_optie(request):
    if request.method == 'POST':
        bestelnr = int(request.POST['bestelnr'])
        email = request.POST['usr_email']

        try:
            oude_type = request.POST['huidig_type']
        except KeyError:
            oude_type = request.POST['prod_type']

        if request.POST['done'] == 'Verwijder bestelling':
            producten_array = (bests.find_one({'bestelnr': bestelnr}, {'producten': 1}))['producten']

            for product in producten_array:
                prod_naam = product['product']
                inc_doc = {}

                try:
                    snijden = product['snijden']
                    inc_doc['gewicht'] = int(product['gewicht']) * -1
                    for gewicht, aantal in snijden.items():
                        inc_doc['snijden.' + gewicht] = int(aantal) * -1

                except KeyError:
                    cat_doc = prods.find_one({'product': prod_naam})
                    cat = cat_doc['cat']
                    if cat == 'zelf_gourmet':
                        for prod, aantal in product['conf'].items():
                            inc_doc['conf.' + prod] = int(aantal) * -1

                    elif cat == 'dry_aged':
                        inc_doc[product['soort']] = int(product['gewicht']) * -1

                    elif cat == 'menu':
                        aantal = int(product['aantal'])
                        inc_doc['aantal'] = aantal * -1

                        for gerecht, nummer in product['voorgerecht'].items():
                            inc_doc['voorgerecht.' + gerecht] = int(nummer) * -1

                        inc_doc['hoofdgerecht.beef_wellington'] = aantal * -1
                        inc_doc['dessert.dessert_buffet'] = aantal * -1

                    else:
                        inc_doc['aantal'] = int(product['aantal']) * -1

                try:
                    bijz = product['bijz']
                    print('nu ga ik verwijderen')

                    result = prods.update_one({'product': prod_naam}, {'$inc': inc_doc,
                                                                       '$pull': {'bijz': {str(bestelnr): bijz}}})

                    print(result.raw_result)
                except KeyError:
                    prods.update_one({'product': prod_naam}, {'$inc': inc_doc})

            bests.delete_one({'bestelnr': bestelnr})
            return HttpResponseRedirect('/')

        elif request.POST['done'] == 'Nieuw product toevoegen':
            return render(request, 'nieuwApp/nieuwProduct.html', {
                'nieuw_prod': request.POST['product'],
                'gekozen_type': oude_type,
                'passed_bestelnr': bestelnr,
                'passed_email': email,
                'form': ProductForm()
            })

        elif request.POST['done'] == 'Ander type product':
            nieuw_type = request.POST['prod_type']
            return render(request, 'nieuwApp/gekozenNieuw.html', {
                'gekozen_type': nieuw_type,
                'passed_bestelnr': bestelnr,
                'passed_email': email,
                'products_list': prod_list,
                'product_form': kies_form(nieuw_type),
                'speciale_optie_form': SpecialeOptieForm(),
                'huidige_producten': huidig_producten(bestelnr)
            })
        elif request.POST['done'] == 'Negeren en afronden':
            if huidig_producten(bestelnr) == 'Nog geen producten toegevoegd':
                return render(request, 'nieuwApp/gekozenNieuw.html', {
                    'gekozen_type': oude_type,
                    'passed_bestelnr': bestelnr,
                    'passed_email': email,
                    'products_list': prod_list,
                    'product_form': kies_form(oude_type),
                    'speciale_optie_form': SpecialeOptieForm(),
                    'huidige_producten': huidig_producten(bestelnr)
                })
            else:
                return render(request, 'nieuwApp/bestellingAfmaken.html', {
                    'passed_bestelnr': bestelnr,
                    'passed_email': email,
                    'form': BestellingAfmakenForm(),
                    'speciale_optie_form': SpecialeOptieForm(),
                    'huidige_producten': huidig_producten(bestelnr)
                })

    else:
        return HttpResponse('Gozer, wat annoying dit is niet de bedoeling. Ga lekker naar een andere pagina mijn amice.')


def nieuw_keuze(request):
    if request.method == 'POST':
        bestelnr = int(request.POST['bestelnr'])
        email = request.POST['usr_email']
        oude_type = request.POST['huidig_type']
        nieuw_type = request.POST['prod_type']

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
                    'product_form': SnijdForm(),
                    'speciale_optie_form': SpecialeOptieForm(),
                    'huidige_producten': huidig_producten(bestelnr)
                })

        elif oude_type == 'menu':
            form = MenuForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data

                v_gerecht_doc = {}

                int_carp = int(data['carpaccio'])
                int_ragout = int(data['kalfsragout'])

                if int_carp > 0: v_gerecht_doc['carpaccio'] = int_carp
                if int_ragout > 0: v_gerecht_doc['kalfsragout'] = int_ragout

                Menu('traditioneel_kerstmenu', int(data['aantal']), v_gerecht_doc, 'beef_wellington', 'dessert_buffet', data['bijz']).insert(bestelnr)

            else:
                return render(request, 'nieuwApp/gekozenNieuw.html', {
                    'error_message': 'Oeps, er is iets mis gegaan. Waarschijnlijk heb je niet een menu-product gekozen.',
                    'gekozen_type': oude_type,
                    'passed_bestelnr': bestelnr,
                    'passed_email': email,
                    'products_list': prod_list,
                    'product_form': form,
                    'speciale_optie_form': SpecialeOptieForm(),
                    'huidige_producten': huidig_producten(bestelnr)
                })

        elif oude_type == 'zelf_gourmet':
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
                    if int_optie > 0: conf_doc[optie.replace("_", " ")] = int_optie

                Gourmet('zelf_gourmet', conf_doc, data['bijz']).insert(bestelnr)
            else:
                return render(request, 'nieuwApp/gekozenNieuw.html', {
                    'error_message': 'Oeps, er is iets mis gegaan. Check je inputs en probeer het aub opnieuw.',
                    'gekozen_type': oude_type,
                    'passed_bestelnr': bestelnr,
                    'passed_email': email,
                    'products_list': prod_list,
                    'product_form': form,
                    'speciale_optie_form': SpecialeOptieForm(),
                    'huidige_producten': huidig_producten(bestelnr)
                })

        elif oude_type == 'dry_aged':
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
                    'product_form': form,
                    'speciale_optie_form': SpecialeOptieForm(),
                    'huidige_producten': huidig_producten(bestelnr)
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
                    'product_form': form,
                    'speciale_optie_form': SpecialeOptieForm(),
                    'huidige_producten': huidig_producten(bestelnr)
                })

        if request.POST['done'] == 'Afronden':
            return render(request, 'nieuwApp/bestellingAfmaken.html', {
                'passed_bestelnr': bestelnr,
                'passed_email': email,
                'form': BestellingAfmakenForm(),
                'speciale_optie_form': SpecialeOptieForm(),
                'huidige_producten': huidig_producten(bestelnr)
            })
        else:
            return render(request, 'nieuwApp/gekozenNieuw.html', {
                'gekozen_type': nieuw_type,
                'passed_bestelnr': bestelnr,
                'passed_email': email,
                'products_list': prod_list,
                'product_form': kies_form(nieuw_type),
                'speciale_optie_form': SpecialeOptieForm(),
                'huidige_producten': huidig_producten(bestelnr)
            })

    else:
        return HttpResponse(
            "sjongejonge dit is niet de bedoeling, hup ga weer terug naar home, toe maar, ga dan, komaan, tempo please")
