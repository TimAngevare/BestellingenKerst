from django.db import models
import pprint

TYPES = ['snijdvlees', 'menu', 'gourmet','formaat', 'bronvlees']

from utils import get_db
kerst_db = get_db('kerst_db')
bests = kerst_db['bestellingen']

class Snijdvlees:
    def __init__(self, product, cat, gewicht, snijden, bijz):
        self.product = product
        self.cat = cat
        self.gewicht = gewicht
        self.snijden = snijden
        self.bijz = bijz
    
    def insert(self, bestelnr):
        new_doc = {
            'product': self.product,
            'cat': self.cat,
            'gewicht': self.gewicht,
            'snijden': self.snijden,
        }

        if self.bijz:
            new_doc['bijz'] = self.bijz

        bests.update_one({'bestelnr': bestelnr}, {"$push" : {"producten" : new_doc}})

class Menu:
    def __init__(self, product, cat, aantal, voorgerecht, hoofdgerecht, dessert, bijz):
        self.product = product
        self.cat = cat
        self.aantal = aantal
        self.voorgerecht = voorgerecht
        self.hoofdgerecht = hoofdgerecht
        self.dessert = dessert
        self.bijz = bijz
    
    def insert(self, bestelnr):
        new_doc = {
            'product': self.product,
            'cat': self.cat,
            'aantal': self.aantal,
            'voorgerecht': self.voorgerecht,
            'hoofdgerecht': self.hoofdgerecht,
            'dessert': self.dessert,
        }

        if self.bijz:
            new_doc['bijz'] = self.bijz

        bests.update_one({'bestelnr': bestelnr}, {"$push" : {"producten" : new_doc}})

class Gourmet:
    def __init__(self, product, cat, conf, bijz):
        self.product = product
        self.cat = cat
        self.conf = conf
        self.bijz = bijz
    
    def insert(self, bestelnr):
        new_doc = {
            'product': self.product,
            'cat': self.cat,
            'conf': self.conf,
        }

        if self.bijz:
            new_doc['bijz'] = self.bijz

        bests.update_one({'bestelnr': bestelnr}, {"$push" : {"producten" : new_doc}})

class Formaat:
    def __init__(self, product, cat, formaat, aantal, bijz):
        self.product = product
        self.cat = cat
        self.formaat = formaat
        self.aantal = aantal
        self.bijz = bijz
    
    def insert(self, bestelnr):
        new_doc = {
            'product': self.product,
            'cat': self.cat,
            'formaat': self.formaat,
            'aantal': self.aantal
        }

        if self.bijz:
            new_doc['bijz'] = self.bijz

        bests.update_one({'bestelnr': bestelnr}, {"$push" : {"producten" : new_doc}})

class BronVlees:
    def __init__(self, product, bron, gewicht, bijz):
        self.product = product
        self.bron = bron
        self.gewicht = gewicht
        self.bijz = bijz
    
    def insert(self, bestelnr):
        new_doc = {
            'product': self.product,
            'bron': self.bron,
            'gewicht': self.gewicht,
        }

        if self.bijz:
            new_doc['bijz'] = self.bijz

        bests.update_one({'bestelnr': bestelnr}, {"$push" : {"producten" : new_doc}})

class Standaard:
    def __init__(self, product, cat, aantal, bijz):
        self.product = product
        self.cat = cat,
        self.aantal = aantal
        self.bijz = bijz
    
    def insert(self, bestelnr):
        new_doc = {
            'product': self.product,
            'cat': self.cat,
            'aantal': self.aantal,
        }

        if self.bijz:
            new_doc['bijz'] = self.bijz

        bests.update_one({'bestelnr': bestelnr}, {"$push" : {"producten" : new_doc}})