import os
from utils import get_db

kerst_db = get_db(os.environ['MONGODB'])
prods = kerst_db['producten']
bests = kerst_db['bestellingen']


def verwijder_best_tui():
    bestelnr = int(input('\nBestelnummer van de bestelling die je wil verwijderen -'))
    delete_result = bests.delete_one({'bestelnr': bestelnr})
    if delete_result.acknowledged:
        if delete_result.deleted_count == 1:
            print("Gelukt!")
        else:
            print("Er zijn " + delete_result.deleted_count + " documenten verwijderd uit bestellingen.")
    else:
        print("Het gaat helemaal mis, het is niet gelukt.")


def verwijder_best(bestelnr):
    delete_result = bests.delete_one({'bestelnr': bestelnr})
    if delete_result.acknowledged:
        if delete_result.deleted_count != 1:
            raise RuntimeError("Verwijderen gelukt, maar er is niet 1 bestelling verwijderd maar " + delete_result.deleted_count)
    else:
        raise RuntimeError("Het verwijderen van de bestelling is niet gelukt: unacknowledged")


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


# menu_opties = {
#     '1': verwijder_best_tui,
#     '2': cat_toevoegen_tui
# }
#
# menu_text = """
# 1: Verwijder bestelling
# 2: Categorieen toevoegen
#
# 9: Stop"""
#
# while True:
#     print(menu_text)
#     keuze = input('Wat wil je doen? -')
#     if keuze == '9':
#         break
#     else:
#         menu_opties[keuze]()
