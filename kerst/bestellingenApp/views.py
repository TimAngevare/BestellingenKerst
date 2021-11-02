from django.shortcuts import render
from django.http import HttpResponse

from utils import get_db
kerst_db = get_db('kerst_db')
best = kerst_db['bestellingen']

def index(request):
    return render(request, 'main.html')

def nieuw(request):
    return HttpResponse("Hier kan je een nieuwe bestelling opnemen.")

def zoek(request):
    return HttpResponse("Hier kan je zoeken naar een bestelling.")