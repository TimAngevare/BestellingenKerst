from django.shortcuts import render
from django.http import HttpResponse
import pprint

from utils import get_db
kerst_db = get_db('kerst_db')
best = kerst_db['bestellingen']

def index(request):
    return HttpResponse("Hallo, je bent beland bij de root van bestellingenApp.")