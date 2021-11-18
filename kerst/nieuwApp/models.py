# from django.db import models

from utils import get_db

kerst_db = get_db('kerst_db')
bests = kerst_db['bestellingen']
prods = kerst_db['producten']


class Product:
    def __init__(self, product, cat):
        self.product = product
        self.cat = cat

    def insert(self):
        prods.insert_one({"product": self.product, "cat": self.cat})


class Snijdvlees:
    def __init__(self, product, gewicht, snijden, bijz):
        self.product = product
        self.gewicht = gewicht
        self.snijden = snijden
        self.bijz = bijz

    def insert(self, bestelnr):
        new_doc = {
            'product': self.product,
            'gewicht': self.gewicht,
            'snijden': self.snijden,
        }

        incs = {'gewicht': self.gewicht}

        for key, value in self.snijden.items():
            nieuw_key = 'snijden.' + key
            incs[nieuw_key] = value

        if self.bijz:
            new_doc['bijz'] = self.bijz
            prods.update_one({'product': self.product},
                             {'$inc': incs,
                              '$set': {'bijz.' + str(bestelnr): self.bijz}},
                             upsert=True)
        else:
            prods.update_one({'product': self.product}, {'$inc': incs}, upsert=True)

        bests.update_one({'bestelnr': bestelnr}, {"$push": {"producten": new_doc}})


class Menu:
    def __init__(self, product, aantal, voorgerecht, hoofdgerecht, dessert, bijz):
        self.product = product
        self.aantal = aantal
        self.voorgerecht = voorgerecht
        self.hoofdgerecht = hoofdgerecht
        self.dessert = dessert
        self.bijz = bijz

    def insert(self, bestelnr):
        new_doc = {
            'product': self.product,
            'aantal': self.aantal,
            'voorgerecht': self.voorgerecht,
            'hoofdgerecht': self.hoofdgerecht,
            'dessert': self.dessert,
        }

        if self.bijz:
            new_doc['bijz'] = self.bijz

        bests.update_one({'bestelnr': bestelnr}, {"$push": {"producten": new_doc}})

        incs = {'aantal': self.aantal}

        for key, value in self.voorgerecht.items():
            nieuw_key = 'voorgerecht.' + key
            incs[nieuw_key] = value

        incs['hoofdgerecht.beef_wellington'] = self.aantal
        incs['dessert.dessert_buffet'] = self.aantal

        if self.bijz:
            prods.update_one({'product': self.product},
                             {'$inc': incs,
                              '$set': {
                                  'bijz.' + str(bestelnr): self.bijz,
                                  'cat': 'menu'}},
                             upsert=True)
        else:
            prods.update_one({'product': self.product},
                             {'$inc': incs,
                              '$set': {'cat': 'menu'}},
                             upsert=True)


class Gourmet:
    def __init__(self, product, conf, bijz):
        self.product = product
        self.conf = conf
        self.bijz = bijz

    def insert(self, bestelnr):
        new_doc = {
            'product': self.product,
            'conf': self.conf,
        }

        incs = {}

        for key, value in self.conf.items():
            nieuw_key = 'conf.' + key
            incs[nieuw_key] = value

        if self.bijz:
            new_doc['bijz'] = self.bijz
            prods.update_one({'product': self.product},
                             {'$inc': incs,
                              '$set': {'bijz.' + str(bestelnr): self.bijz,
                                       'cat': 'zelf_gourmet'}},
                             upsert=True)
        else:
            prods.update_one({'product': self.product},
                             {'$inc': incs,
                              '$set': {'cat': 'zelf_gourmet'}},
                             upsert=True)

        bests.update_one({'bestelnr': bestelnr}, {"$push": {"producten": new_doc}})


class DryAgedVlees:
    def __init__(self, product, soort, gewicht, bijz):
        self.product = product
        self.soort = soort
        self.gewicht = gewicht
        self.bijz = bijz

    def insert(self, bestelnr):
        new_doc = {
            'product': self.product,
            'soort': self.soort,
            'gewicht': self.gewicht,
        }

        incs = {self.soort: self.gewicht}

        if self.bijz:
            new_doc['bijz'] = self.bijz
            prods.update_one({'product': self.product},
                             {'$inc': incs,
                              '$set': {
                                  'bijz.' + str(bestelnr): self.bijz,
                                  'cat': 'dry_aged'
                              }},
                             upsert=True)
        else:
            prods.update_one({'product': self.product},
                             {'$inc': incs,
                              '$set': {'cat': 'dry_aged'}},
                             upsert=True)

        bests.update_one({'bestelnr': bestelnr}, {"$push": {"producten": new_doc}})


class Standaard:
    def __init__(self, product, aantal, bijz):
        self.product = product
        self.aantal = aantal
        self.bijz = bijz

    def insert(self, bestelnr):
        new_doc = {
            'product': self.product,
            'aantal': self.aantal,
        }

        incs = {'aantal': self.aantal}

        if self.bijz:
            new_doc['bijz'] = self.bijz
            prods.update_one({'product': self.product}, {'$inc': incs, '$set': {'bijz.' + str(bestelnr): self.bijz}},
                             upsert=True)
        else:
            prods.update_one({'product': self.product}, {'$inc': incs}, upsert=True)

        bests.update_one({'bestelnr': bestelnr}, {"$push": {"producten": new_doc}})
