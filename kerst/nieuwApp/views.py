from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages

import datetime

from .models import *
from .forms import *

from mongo_manage import get_datalists

alle_prodlist, standaard_prodlist, snijdvlees_prodlist, cat_list = get_datalists()


def index(request):
    return render(request, 'main.html', {
        "mainpage": True,
        "verwijder_form": VerwijderForm
    })


def nieuw(request):
    fav_medewerker = request.COOKIES.get('fav_medewerker')
    if fav_medewerker is not None:
        inits = {'medewerker': fav_medewerker}
    else:
        inits = {}

    return render(request, 'nieuwApp/nieuw.html', {
        'form': NieuweBestellingForm(initial=inits)
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
    elif het_type == 'rollade':
        return RolladeForm()


def kies_prodlist(het_type):
    if het_type == 'snijdvlees':
        return snijdvlees_prodlist
    else:
        return standaard_prodlist


def huidig_producten(bestelnr):
    producten = bests.find_one({'bestelnr': int(bestelnr)}, {'producten': 1})
    return_string = ""
    if len(producten['producten']) > 0:
        for product in producten['producten']:
            try:
                return_string += product['product'] + " (x" + str(product['aantal']) + "), "
            except KeyError:
                try:
                    return_string += product['product'] + " (" + str(product['gewicht']) + " gr.), "
                except KeyError:
                    prod = product['product']
                    if prod == 'zelf_gourmet':
                        prod = 'gourmet eigen conf.'

                    return_string += prod + ", "
    else:
        return_string = "Nog geen producten toegevoegd"

    if return_string[-2:] == ", ":
        return return_string[:-2]

    return return_string


def nieuw_bestel(request):
    if request.method == 'POST':
        form = NieuweBestellingForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            email = data['usr_email'].strip()
            gekozen_type = data['prod_type']
            dag_ophalen = data['dagophalen']

            # Nieuw bestelnummer maken
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
                "bestelnr": nieuw_bestelnr,
                "email": email,
                "state": "niet_gestart",
                "medewerker": data['medewerker'],
                "producten": []
            }
            bests.insert_one(doc)

            response = render(request, 'nieuwApp/gekozenNieuw.html', {
                'gekozen_type': gekozen_type,
                'passed_bestelnr': nieuw_bestelnr,
                'passed_email': email,
                'products_list': kies_prodlist(gekozen_type),
                'product_form': kies_form(gekozen_type),
                'speciale_optie_form': SpecialeOptieForm(),
                'huidige_producten': huidig_producten(nieuw_bestelnr)
            })
            response.set_cookie('fav_medewerker', data['medewerker'].strip().lower())
            return response
        else:
            messages.error(request, "Je hebt niet alles ingevuld", extra_tags='w3-red')
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
            return render(request, 'nieuwApp/gekozenNieuw.html', {
                'gekozen_type': prod_type,
                'passed_bestelnr': bestelnr,
                'passed_email': email,
                'products_list': kies_prodlist(prod_type),
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

            messages.success(request, f'Bestelling #{bestelnr} is aangemaakt!', extra_tags='w3-green')
            return HttpResponseRedirect('/')
        else:
            messages.error(request, 'Oeps, er is iets mis. Probeer het aub opnieuw', extra_tags='w3-red')
            return render(request, 'nieuwApp/bestellingAfmaken.html', {
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
                'products_list': kies_prodlist(oude_type),
                'product_form': kies_form(oude_type),
                'speciale_optie_form': SpecialeOptieForm(),
                'huidige_producten': huidig_producten(bestelnr)
            })
        elif form.is_valid():
            data = form.cleaned_data
            nieuw_prod = data['product'].strip().lower()
            cat = data['cat'].strip().lower()
            Product(nieuw_prod, cat, data['snijdvlees']).insert()

            if cat not in cat_list:
                cat_list.append(cat)

            alle_prodlist.append(nieuw_prod)
            if data['snijdvlees']:
                snijdvlees_prodlist.append(nieuw_prod)
            elif data['cat'] not in ['dry_aged', 'menu', 'zelf_gourmet', 'rollade']:
                standaard_prodlist.append(nieuw_prod)

            messages.success(request, f"Product '{nieuw_prod}' ({cat}) is aangemaakt!", extra_tags='w3-green')
            return render(request, 'nieuwApp/gekozenNieuw.html', {
                'gekozen_type': oude_type,
                'passed_bestelnr': bestelnr,
                'passed_email': email,
                'products_list': kies_prodlist(oude_type),
                'product_form': kies_form(oude_type),
                'speciale_optie_form': SpecialeOptieForm(),
                'huidige_producten': huidig_producten(bestelnr)
            })
        else:
            messages.error(request, 'Oeps, er is iets mis. Probeer het aub opnieuw', extra_tags='w3-red')
            return render(request, 'nieuwApp/nieuwProduct.html', {
                'nieuw_prod': request.POST['product'],
                'gekozen_type': oude_type,
                'passed_bestelnr': bestelnr,
                'passed_email': email,
                'form': form,
                'cat_list': cat_list
            })
    else:
        return HttpResponse("Gast dit kan niet jonge")


def speciale_optie(request):
    if request.method == 'POST':
        bestelnr = int(request.POST['bestelnr'])

        # Bestelling verwijderen, kan vanaf meerdere paginas komen
        if request.POST['done'] == 'Verwijder bestelling':
            find_result = bests.find_one({'bestelnr': bestelnr}, {'producten': 1})

            if not find_result:
                messages.error(request, f'Bestelling #{str(bestelnr)} bestaat niet, dus is niet verwijderd.', extra_tags='w3-red')
                return HttpResponseRedirect('/')

            producten_array = find_result['producten']

            # Eerst alle producten verwijderen
            for product in producten_array:
                prod_naam = product['product']
                inc_doc = {}

                cat = prods.find_one({'product': prod_naam})['cat']

                if cat == 'zelf_gourmet':
                    for prod, doc in product['conf'].items():
                        ding = next(iter(doc))
                        inc_doc['conf.' + prod + '.' + ding] = int(doc[ding]) * -1
                        inc_doc['conf_detail.' + prod + '.' + ding + '.' + str(bestelnr)] = int(doc[ding]) * -1

                elif cat == 'dry_aged':
                    inc_doc[product['soort']] = int(product['gewicht']) * -1

                    # Huidige implementatie
                    inc_doc[product['soort'] + '_detail.' + str(bestelnr)] = int(product['gewicht']) * -1

                    # Implementatie voor snijden bij dry_aged
                    # snijden = product['snijden']
                    # for gewicht, aantal in snijden.items():
                    #     inc_doc['snijden.' + gewicht] = int(aantal) * -1
                    #     inc_doc[product['soort'] + '_detail.' + gewicht + '.' + str(bestelnr)] = int(aantal) * -1

                elif cat == 'menu':
                    aantal = int(product['aantal'])
                    inc_doc['aantal'] = aantal * -1

                    for gerecht, nummer in product['voorgerecht'].items():
                        inc_doc['voorgerecht.' + gerecht] = int(nummer) * -1
                        inc_doc['menu_detail.' + gerecht + '.' + str(bestelnr)] = int(nummer) * -1

                    inc_doc['hoofdgerecht.beef_wellington'] = aantal * -1
                    inc_doc['menu_detail.beef_wellington.' + str(bestelnr)] = aantal * -1

                    inc_doc['dessert.dessert_buffet'] = aantal * -1
                    inc_doc['menu_detail.dessert_buffet.' + str(bestelnr)] = aantal * -1

                elif cat == 'rollade':
                    int_gewicht_neg = int(product['gewicht']) * -1
                    inc_doc['gewicht'] = int_gewicht_neg

                    if product['gekruid']:
                        inc_doc['gekruid.ja'] = int_gewicht_neg
                        inc_doc['gekruid_detail.ja.' + str(bestelnr)] = int_gewicht_neg
                    else:
                        inc_doc['gekruid.nee'] = int_gewicht_neg
                        inc_doc['gekruid_detail.nee.' + str(bestelnr)] = int_gewicht_neg

                else:
                    try:
                        snijden = product['snijden']
                        inc_doc['gewicht'] = int(product['gewicht']) * -1
                        for gewicht, aantal in snijden.items():
                            inc_doc['snijden.' + gewicht] = int(aantal) * -1
                            inc_doc['snijden_detail.' + gewicht + '.' + str(bestelnr)] = int(aantal) * -1

                    except KeyError:
                        inc_doc['aantal'] = int(product['aantal']) * -1
                        inc_doc['detail.' + str(bestelnr)] = int(product['aantal']) * -1

                # In 1 keer checken of dat er een bijzonderheid is
                try:
                    bijz = product['bijz']

                    result = prods.update_one({'product': prod_naam}, {'$inc': inc_doc,
                                                                       '$pull': {'bijz': {str(bestelnr): bijz}}})

                    print(result.raw_result)
                except KeyError:
                    prods.update_one({'product': prod_naam}, {'$inc': inc_doc})

            # Nog even de bestelling zelf verwijderen en dan klaar!
            bests.delete_one({'bestelnr': bestelnr})
            messages.success(request, f'Bestelling #{str(bestelnr)} is verwijderd!', extra_tags='w3-green')
            return HttpResponseRedirect('/')

        # Vanaf hier komt het altijd met de context van email en het type
        email = request.POST['usr_email']

        try:
            oude_type = request.POST['huidig_type']
        except KeyError:
            oude_type = request.POST['prod_type']

        if request.POST['done'] == 'Nieuw product toevoegen':
            return render(request, 'nieuwApp/nieuwProduct.html', {
                'nieuw_prod': request.POST['product'],
                'gekozen_type': oude_type,
                'passed_bestelnr': bestelnr,
                'passed_email': email,
                'form': ProductForm(),
                'cat_list': cat_list
            })

        elif request.POST['done'] == 'Nieuw product':
            return render(request, 'nieuwApp/nieuwProduct.html', {
                'gekozen_type': oude_type,
                'passed_bestelnr': bestelnr,
                'passed_email': email,
                'form': ProductForm(),
                'cat_list': cat_list
            })

        elif request.POST['done'] == 'Nog een product':
            nieuw_type = request.POST['prod_type']
            return render(request, 'nieuwApp/gekozenNieuw.html', {
                'gekozen_type': nieuw_type,
                'passed_bestelnr': bestelnr,
                'passed_email': email,
                'products_list': kies_prodlist(nieuw_type),
                'product_form': kies_form(nieuw_type),
                'speciale_optie_form': SpecialeOptieForm(),
                'huidige_producten': huidig_producten(bestelnr)
            })
        elif request.POST['done'] == 'Negeren en afronden':
            if huidig_producten(bestelnr) == 'Nog geen producten toegevoegd':
                messages.error(request, 'Je hebt nog geen producten toegevoegd, dus je kan de bestelling ook niet afronden', extra_tags='w3-red')
                return render(request, 'nieuwApp/gekozenNieuw.html', {
                    'gekozen_type': oude_type,
                    'passed_bestelnr': bestelnr,
                    'passed_email': email,
                    'products_list': kies_prodlist(oude_type),
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

        if request.POST['product'] not in alle_prodlist:
            messages.info(request, 'Dit product staat nog niet in de database, vul dit in om het toe te voegen', extra_tags='w3-blue')
            return render(request, 'nieuwApp/nieuwProduct.html', {
                'nieuw_prod': request.POST['product'],
                'gekozen_type': oude_type,
                'passed_bestelnr': bestelnr,
                'passed_email': email,
                'form': ProductForm(),
                'cat_list': cat_list
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
                messages.error(request, 'Oeps, er is iets mis. Probeer het aub opnieuw', extra_tags='w3-red')
                return render(request, 'nieuwApp/gekozenNieuw.html', {
                    'gekozen_type': oude_type,
                    'passed_bestelnr': bestelnr,
                    'passed_email': email,
                    'products_list': kies_prodlist(oude_type),
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
                messages.error(request, 'Oeps, er is iets mis. Probeer het aub opnieuw', extra_tags='w3-red')
                return render(request, 'nieuwApp/gekozenNieuw.html', {
                    'gekozen_type': oude_type,
                    'passed_bestelnr': bestelnr,
                    'passed_email': email,
                    'products_list': kies_prodlist(oude_type),
                    'product_form': form,
                    'speciale_optie_form': SpecialeOptieForm(),
                    'huidige_producten': huidig_producten(bestelnr)
                })

        elif oude_type == 'zelf_gourmet':
            form = GourmetForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                conf_doc = {}
                menu_items = ['ba_cheddar', 'ba_hamburgers', 'bavette', 'chinese_roaststeak', 'chipolata',
                              'diamanthaas', 'dry_aged', 'hamburger', 'kalfsoester', 'kip_bacon_chili', 'kipfilet',
                              'kogel_biefstuk', 'lamsrack', 'ossenhaaspuntjes', 'rundervink', 'shoarma', 'slavink',
                              'speklapjes', 'varkenshaas', 'varkenshaassate']

                for optie in menu_items:
                    int_optie = int(data[optie])

                    if int_optie > 0:
                        gemarineerd = data[optie + '_mar']
                        if gemarineerd:
                            conf_doc[optie] = {"gem": int_optie}
                        else:
                            conf_doc[optie] = {"nat": int_optie}

                Gourmet('zelf_gourmet', conf_doc, data['bijz']).insert(bestelnr)
            else:
                messages.error(request, 'Oeps, er is iets mis. Probeer het aub opnieuw', extra_tags='w3-red')
                return render(request, 'nieuwApp/gekozenNieuw.html', {
                    'gekozen_type': oude_type,
                    'passed_bestelnr': bestelnr,
                    'passed_email': email,
                    'products_list': kies_prodlist(oude_type),
                    'product_form': form,
                    'speciale_optie_form': SpecialeOptieForm(),
                    'huidige_producten': huidig_producten(bestelnr)
                })

        elif oude_type == 'dry_aged':
            form = DryAgedForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                # snijd_string = data['snijden']
                # snijd_komma_splits = snijd_string.split(',')
                # del snijd_komma_splits[-1]
                #
                # snijd_obj = {}
                #
                # for snijdoptie in snijd_komma_splits:
                #     snijdvalue = snijdoptie.split(':')
                #     snijd_obj[snijdvalue[0]] = int(snijdvalue[1])

                DryAgedVlees(data['product'], data['soort'], data['gewicht'], data['bijz']).insert(bestelnr)
            else:
                messages.error(request, 'Oeps, er is iets mis. Probeer het aub opnieuw', extra_tags='w3-red')
                return render(request, 'nieuwApp/gekozenNieuw.html', {
                    'gekozen_type': oude_type,
                    'passed_bestelnr': bestelnr,
                    'passed_email': email,
                    'products_list': kies_prodlist(oude_type),
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
                messages.error(request, 'Oeps, er is iets mis. Probeer het aub opnieuw', extra_tags='w3-red')
                return render(request, 'nieuwApp/gekozenNieuw.html', {
                    'gekozen_type': oude_type,
                    'passed_bestelnr': bestelnr,
                    'passed_email': email,
                    'products_list': kies_prodlist(oude_type),
                    'product_form': form,
                    'speciale_optie_form': SpecialeOptieForm(),
                    'huidige_producten': huidig_producten(bestelnr)
                })

        elif oude_type == 'rollade':
            form = RolladeForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                Rollade(data['product'], data['gewicht'], data['gekruid'], data['bijz']).insert(bestelnr)
            else:
                messages.error(request, 'Oeps, er is iets mis. Probeer het aub opnieuw', extra_tags='w3-red')
                return render(request, 'nieuwApp/gekozenNieuw.html', {
                    'gekozen_type': oude_type,
                    'passed_bestelnr': bestelnr,
                    'passed_email': email,
                    'products_list': kies_prodlist(oude_type),
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
                'products_list': kies_prodlist(nieuw_type),
                'product_form': kies_form(nieuw_type),
                'speciale_optie_form': SpecialeOptieForm(),
                'huidige_producten': huidig_producten(bestelnr)
            })

    else:
        return HttpResponse("dit is niet de bedoeling, ga weer terug naar home")
