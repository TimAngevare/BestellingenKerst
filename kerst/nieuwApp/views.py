from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages

from .models import *
from .forms import *

import mongo_manage as mm

alle_prodlist, standaard_prodlist, snijdvlees_prodlist, cat_list = mm.get_datalists()


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


def nieuw_bestel(request):
    if request.method == 'POST':
        form = NieuweBestellingForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            gekozen_type = data['prod_type']
            email = data['usr_email'].strip()

            # Nieuw bestelnummer maken
            nieuw_bestelnr = mm.maak_nieuwe_bestelling(email, data['dagophalen'], data['medewerker'])

            response = render(request, 'nieuwApp/gekozenNieuw.html', {
                'gekozen_type': gekozen_type,
                'passed_bestelnr': nieuw_bestelnr,
                'passed_email': email,
                'products_list': kies_prodlist(gekozen_type),
                'product_form': kies_form(gekozen_type),
                'speciale_optie_form': SpecialeOptieForm(),
                'huidige_producten': mm.get_huidige_producten(nieuw_bestelnr)
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
                'huidige_producten': mm.get_huidige_producten(bestelnr)
            })

        form = BestellingAfmakenForm(request.POST)
        if form.is_valid():
            mm.finish_bestelling(bestelnr, email, form.cleaned_data)

            messages.success(request, f'Bestelling #{bestelnr} is aangemaakt!', extra_tags='w3-green')
            return HttpResponseRedirect('/')
        else:
            messages.error(request, 'Oeps, er is iets mis. Probeer het aub opnieuw', extra_tags='w3-red')
            return render(request, 'nieuwApp/bestellingAfmaken.html', {
                'passed_bestelnr': request.POST['bestelnr'],
                'passed_email': request.POST['usr_email'],
                'form': BestellingAfmakenForm(),
                'speciale_optie_form': SpecialeOptieForm(),
                'huidige_producten': mm.get_huidige_producten(request.POST['bestelnr'])
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
                'huidige_producten': mm.get_huidige_producten(bestelnr)
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
                'huidige_producten': mm.get_huidige_producten(bestelnr)
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
            verwijder_result = mm.verwijder(bestelnr)

            if not verwijder_result:
                messages.error(request, f'Bestelling #{str(bestelnr)} bestaat niet, dus is niet verwijderd.',
                               extra_tags='w3-red')
                return HttpResponseRedirect('/')
            else:
                messages.success(request, f'Bestelling #{str(bestelnr)} is verwijderd!', extra_tags='w3-green')
                return HttpResponseRedirect('/')

        # Vanaf hier komt het altijd met de context van email en het type
        email = request.POST['usr_email']
        huidige_producten = mm.get_huidige_producten(bestelnr)

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
                'huidige_producten': huidige_producten
            })
        elif request.POST['done'] == 'Negeren en afronden':
            huidige_producten = mm.get_huidige_producten(bestelnr)
            if huidige_producten == 'Nog geen producten toegevoegd':
                messages.error(request, 'Je hebt nog geen producten toegevoegd, dus je kan de bestelling ook niet afronden', extra_tags='w3-red')
                return render(request, 'nieuwApp/gekozenNieuw.html', {
                    'gekozen_type': oude_type,
                    'passed_bestelnr': bestelnr,
                    'passed_email': email,
                    'products_list': kies_prodlist(oude_type),
                    'product_form': kies_form(oude_type),
                    'speciale_optie_form': SpecialeOptieForm(),
                    'huidige_producten': huidige_producten
                })
            else:
                return render(request, 'nieuwApp/bestellingAfmaken.html', {
                    'passed_bestelnr': bestelnr,
                    'passed_email': email,
                    'form': BestellingAfmakenForm(),
                    'speciale_optie_form': SpecialeOptieForm(),
                    'huidige_producten': huidige_producten
                })

    else:
        return HttpResponse('Gozer, wat annoying dit is niet de bedoeling. Ga lekker naar een andere pagina mijn amice.')


def nieuw_keuze(request):
    if request.method == 'POST':
        bestelnr = int(request.POST['bestelnr'])
        email = request.POST['usr_email']
        oude_type = request.POST['huidig_type']
        nieuw_type = request.POST['prod_type']
        huidige_producten = mm.get_huidige_producten(bestelnr)

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
                    'huidige_producten': huidige_producten
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
                    'huidige_producten': huidige_producten
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
                    'huidige_producten': huidige_producten
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
                    'huidige_producten': huidige_producten
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
                    'huidige_producten': huidige_producten
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
                    'huidige_producten': huidige_producten
                })

        if request.POST['done'] == 'Afronden':
            return render(request, 'nieuwApp/bestellingAfmaken.html', {
                'passed_bestelnr': bestelnr,
                'passed_email': email,
                'form': BestellingAfmakenForm(),
                'speciale_optie_form': SpecialeOptieForm(),
                'huidige_producten': huidige_producten
            })
        else:
            return render(request, 'nieuwApp/gekozenNieuw.html', {
                'gekozen_type': nieuw_type,
                'passed_bestelnr': bestelnr,
                'passed_email': email,
                'products_list': kies_prodlist(nieuw_type),
                'product_form': kies_form(nieuw_type),
                'speciale_optie_form': SpecialeOptieForm(),
                'huidige_producten': huidige_producten
            })

    else:
        return HttpResponse("dit is niet de bedoeling, ga weer terug naar home")
