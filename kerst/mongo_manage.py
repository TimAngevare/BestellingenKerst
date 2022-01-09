import datetime
from utils import get_db

kerst_db = get_db('kerst_db')
prods = kerst_db['producten']
bests = kerst_db['bestellingen']

# ------- GLOBAAL GEBRUIKTE FUNCTIES -----------------------------------------------------------------------------------


def verwijder_best(bestelnr):
    delete_result = bests.delete_one({'bestelnr': bestelnr})
    if delete_result.acknowledged:
        if delete_result.deleted_count != 1:
            raise RuntimeError("Verwijderen gelukt, maar er is niet 1 bestelling verwijderd maar " + delete_result.deleted_count)
    else:
        raise RuntimeError("Het verwijderen van de bestelling is niet gelukt: unacknowledged")


def get_huidige_producten(bestelnr):
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


def zoek_prod(dict):
    new_dict = {}
    for key, value in dict.items():
        if key == "product" and value != "":
            del new_dict["cat"]
            new_dict[key] = value
        elif value != '' and value is not None and value != "Alles":
            new_dict[key] = value
    return prods.count_documents(new_dict), prods.find(new_dict)


def zoek_best_alles(dict):
    new_dict = {}
    for key, value in dict.items():
        if value == '' or value == "Alles":
            continue
        elif key == 'dagophalen':
            new_dict['dagophalen'] = str(value)
        else:
            new_dict[key] = value
    return bests.count_documents(new_dict), bests.find(new_dict)


def update_state_best(num, state):
    bests.update_one({'bestelnr': num}, {'$set': {'state': state}}, upsert=False)


def update_state_prod(prod, state):
    prods.update_one({'product': prod}, {'$set': {'state': state}}, upsert=False)


def insert_best(bestelnr, doc, incs, bijz):
    if bijz:
        doc['bijz'] = bijz
        prod_res = prods.update_one({'product': doc["product"]}, {'$inc': incs, '$push': {'bijz': {str(bestelnr): bijz}}})
    else:
        prod_res = prods.update_one({'product': doc["product"]}, {'$inc': incs})

    best_res = bests.update_one({'bestelnr': bestelnr}, {"$push": {"producten": doc}})

    if not best_res.acknowledged or best_res.matched_count != 1:
        raise RuntimeError("Er is iets misgegaan bij het inserten van de bestelling, veranderingen: " + best_res.matched_count)
    elif not prod_res.acknowledged or prod_res.matched_count != 1:
        raise RuntimeError("Er is iets misgegaan bij het inserten van het product, veranderingen: " + prod_res.matched_count)


def insert_prod(product, cat, snijdvlees):
    prod_res = prods.insert_one({"product": product, "cat": cat, "snijdvlees": snijdvlees, "state": "niet_gestart"})

    if not prod_res.acknowledged or prod_res.matched_count != 1:
        raise RuntimeError("Er is iets misgegaan bij het inserten van het product, veranderingen: " + prod_res.matched_count)


def zoek_best(dict):
    new_dict = {}
    for key, value in dict.items():
        if value == '' or value is None:
            continue
        elif key == 'bestelnr':
            new_dict['bestelnr'] = int(value)
        elif key == 'dagophalen':
            new_dict['dagophalen'] = str(value)
        else:
            new_dict.update({key: value})
    return bests.count_documents(new_dict), bests.find(new_dict)


def get_datalists():
    alle_prodlist = []
    standaard_prodlist = []
    snijdvlees_prodlist = []
    cat_list = ["overig"]

    obj_prods = prods.find({}, {'product': 1, 'snijdvlees': 1, 'cat': 1})
    for obj_prod in obj_prods:
        alle_prodlist.append(obj_prod['product'])
        if obj_prod['cat'] not in cat_list:
            cat_list.append(obj_prod['cat'])

        if obj_prod['cat'] in ['dry_aged', 'menu', 'zelf_gourmet', 'rollade']:
            continue

        if obj_prod['snijdvlees']:
            snijdvlees_prodlist.append(obj_prod['product'])
        else:
            standaard_prodlist.append(obj_prod['product'])

    return alle_prodlist, standaard_prodlist, snijdvlees_prodlist, cat_list


def find(db, match_filter, show_filters):
    show_filter = {}
    for filt in show_filters:
        show_filter[filt] = 1

    if db == 'bestellingen':
        return bests.find(match_filter, show_filter)
    elif db == 'producten':
        return prods.find(match_filter, show_filter)
    else:
        raise ValueError("Dat type database is niet bekend binnen het systeem")


def verwijder(bestelnr):
    find_result = find('bestellingen', {'bestelnr': bestelnr}, ['producten'])

    if not find_result:
        return False

    producten_array = find_result['producten']

    # Eerst alle producten verwijderen
    for product in producten_array:
        prod_naam = product['product']
        inc_doc = {}

        cat = find('producten', {'product': prod_naam}, [])['cat']

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

            verw_result = prods.update_one({'product': prod_naam}, {'$inc': inc_doc,
                                                               '$pull': {'bijz': {str(bestelnr): bijz}}})
        except KeyError:
            verw_result = prods.update_one({'product': prod_naam}, {'$inc': inc_doc})


    # Nog even de bestelling zelf verwijderen en dan klaar!
    bests.delete_one({'bestelnr': bestelnr})
    return True


def maak_nieuwe_bestelling(email, dag_ophalen, medewerker):
    obj_bestelnrs = find('bestellingen', {}, ['bestelnr'])
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
        "medewerker": medewerker,
        "producten": []
    }
    bests.insert_one(doc)


def finish_bestelling(bestelnr, email, data):
    bests.update_one({'bestelnr': int(bestelnr)}, {
        "$set": {"email": email,
                 "naam": data['naam'],
                 "telnr": data['telnr'],
                 "dagophalen": bestelnr[:2],
                 "tijdophalen": int(data['tijdophalen']),
                 "besteltijd": datetime.datetime.utcnow()
                 }
    })


# ------- TUI ----------------------------------------------------------------------------------------------------------


def verwijder_best_tui():
    bestelnr = int(input('\nBestelnummer van de bestelling die je wil verwijderen -'))
    delete_result = verwijder(bestelnr)

    if bestelnr:
        print('Gelukt!')
    else:
        print('Niet gelukt')


def huidige_producten_tui():
    return get_huidige_producten(int(input("Bestelnummer: ")))


def cat_toevoegen_tui():
    obj_geen_cat = []
    for obj in prods.find({'cat': {'$exists': False}}):
        obj_geen_cat.append(obj)

    while True:
        try:
            obj = obj_geen_cat[0]
        except IndexError:
            print('Je hebt alle producten gehad!')
            break

        product = obj['product']

        cat = input('\nDe categorie van ' + product + " - ")
        update_result = prods.update_one({'product': product}, {'$set': {'cat': cat}})

        if update_result.acknowledged and update_result.modified_count == 1:
            print('Gelukt, de categorie van ' + product + " is nu " + cat + "!")
        else:
            print("Er is iets fout gegaan.")

        obj_geen_cat.remove(obj)

        door = input('Wil je nog een categorie toevoegen (y/n) - ')
        if door != 'y':
            break


def main():
    menu_opties = {
        '1': verwijder_best_tui,
        '2': cat_toevoegen_tui,
        '3': huidige_producten_tui
    }

    menu_text = """
    1: Verwijder bestelling
    2: Categorieen toevoegen
    3: Huidige producten bestelling
    
    9: Stop"""

    while True:
        print(menu_text)
        keuze = input('Wat wil je doen? -')
        if keuze == '9':
            break
        else:
            menu_opties[keuze]()


# if __name__ == "main":
#     main()
