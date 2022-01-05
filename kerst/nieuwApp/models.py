# from django.db import models

from mongo_manage import insert_best, insert_prod


class Product:
    def __init__(self, product, cat, snijdvlees):
        self.product = product
        self.cat = cat
        self.snijdvlees = snijdvlees

    def insert(self):
        insert_prod(self.product, self.cat, self.snijdvlees)


class Snijdvlees:
    def __init__(self, product, gewicht, snijden, bijz):
        self.product = product
        self.gewicht = gewicht
        self.snijden = snijden
        self.bijz = bijz

    def insert(self, bestelnr):
        new_doc = {
            'state': 'niet_gestart',
            'product': self.product,
            'gewicht': self.gewicht,
            'snijden': self.snijden,
        }

        incs = {'gewicht': self.gewicht}

        for key, value in self.snijden.items():
            nieuw_key = 'snijden.' + key
            incs[nieuw_key] = value

            detail_key = 'snijden_detail.' + str(key) + '.' + str(bestelnr)
            incs[detail_key] = value

        insert_best(bestelnr, new_doc, incs, self.bijz)


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
            'state': 'niet_gestart',
            'product': self.product,
            'aantal': self.aantal,
            'voorgerecht': self.voorgerecht,
            'hoofdgerecht': self.hoofdgerecht,
            'dessert': self.dessert,
        }

        if self.bijz:
            new_doc['bijz'] = self.bijz

        incs = {'aantal': self.aantal}

        for key, value in self.voorgerecht.items():
            nieuw_key = 'voorgerecht.' + key
            incs[nieuw_key] = value
            incs['menu_detail.' + key + '.' + str(bestelnr)] = value

        incs['hoofdgerecht.beef_wellington'] = self.aantal
        incs['menu_detail.beef_wellington.' + str(bestelnr)] = self.aantal

        incs['dessert.dessert_buffet'] = self.aantal
        incs['menu_detail.dessert_buffet.' + str(bestelnr)] = self.aantal

        insert_best(bestelnr, new_doc, incs, self.bijz)


class Gourmet:
    def __init__(self, product, conf, bijz):
        self.product = product
        self.conf = conf
        self.bijz = bijz

    def insert(self, bestelnr):
        new_doc = {
            'state': 'niet_gestart',
            'product': self.product,
            'conf': self.conf,
        }

        incs = {}

        for prod_naam, gemar in self.conf.items():
            ding = next(iter(gemar))
            incs['conf.' + prod_naam + '.' + ding] = gemar[ding]
            incs['conf_detail.' + prod_naam + '.' + ding + '.' + str(bestelnr)] = gemar[ding]

        insert_best(bestelnr, new_doc, incs, self.bijz)


class DryAgedVlees:
    def __init__(self, product, soort, gewicht, bijz):
        self.product = product
        self.soort = soort
        self.gewicht = gewicht
        self.bijz = bijz

    def insert(self, bestelnr):
        new_doc = {
            'state': 'niet_gestart',
            'product': self.product,
            'soort': self.soort,
            'gewicht': self.gewicht,
            # 'snijden': self.snijden
        }

        incs = {self.soort: int(self.gewicht), self.soort + '_detail.' + str(bestelnr): int(self.gewicht)}

        insert_best(bestelnr, new_doc, incs, self.bijz)


class Standaard:
    def __init__(self, product, aantal, bijz):
        self.product = product
        self.aantal = aantal
        self.bijz = bijz

    def insert(self, bestelnr):
        new_doc = {
            'product': self.product,
            'aantal': self.aantal,
            'state': 'niet_gestart'
        }

        incs = {'aantal': self.aantal, 'detail.' + str(bestelnr): self.aantal}

        insert_best(bestelnr, new_doc, incs, self.bijz)


class Rollade:
    def __init__(self, product, gewicht, gekruid, bijz):
        self.product = product
        self.gewicht = gewicht
        self.gekruid = gekruid
        self.bijz = bijz

    def insert(self, bestelnr):
        new_doc = {
            'product': self.product,
            'gewicht': self.gewicht,
            'gekruid': self.gekruid,
            'state': 'niet_gestart'
        }

        incs = {'gewicht': self.gewicht}

        if self.gekruid:
            incs['gekruid.ja'] = self.gewicht
            incs['gekruid_detail.ja.' + str(bestelnr)] = self.gewicht
        else:
            incs['gekruid.nee'] = self.gewicht
            incs['gekruid_detail.nee.' + str(bestelnr)] = self.gewicht

        insert_best(bestelnr, new_doc, incs, self.bijz)
