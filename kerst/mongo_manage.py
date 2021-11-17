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


def zoek_best(num, tel, dag):
    if num != '' and tel != '' and dag != '':
        zoek_best.resultaten = bests.find({'bestelnr': int(num), 'dagophalen': dag, 'telnr': tel})
    elif num == '' and dag == '':
        zoek_best.resultaten = bests.find({'telnr': tel})
    elif num == '' and tel == '':
        zoek_best.resultaten = bests.find({'dagophalen': dag})
    elif dag == '' and tel == '':
        zoek_best.resultaten = bests.find({'bestelnr': int(num)})
    elif num == '':
        zoek_best.resultaten = bests.find({'dagophalen': dag, 'telnr': tel})
    elif tel == '':
        zoek_best.resultaten = bests.find({'bestelnr': int(num), 'dagophalen': dag})
    elif dag == '':
        zoek_best.resultaten = bests.find({'bestelnr': int(num), 'telnr': tel})
    else:
        zoek_best.resultaten = 1


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
