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
        