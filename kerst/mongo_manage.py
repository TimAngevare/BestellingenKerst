from utils import get_db

kerst_db = get_db('kerst_db')
prods = kerst_db['producten']
bests = kerst_db['bestellingen']


def verwijder_best():
    bestelnr = int(input('\nBestelnummer van de bestelling die je wil verwijderen -'))
    delete_result = bests.delete_one({'bestelnr': bestelnr})
    if delete_result.acknowledged:
        if delete_result.deleted_count == 1:
            print("Gelukt!")
        else:
            print("Er zijn " + delete_result.deleted_count + " documenten verwijderd uit bestellingen.")
    else:
        print("Het gaat helemaal mis, het is niet gelukt.")


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


def cat_toevoegen():
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


menu_opties = {
    '1': verwijder_best,
    '2': cat_toevoegen
}

menu_text = """
1: Verwijder bestelling
2: Categorieen toevoegen

9: Stop"""

# while True:
#     print(menu_text)
#     keuze = input('Wat wil je doen? -')
#     if keuze == '9':
#         break
#     else:
#         menu_opties[keuze]()
