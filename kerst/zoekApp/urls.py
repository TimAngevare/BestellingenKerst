from django.urls import path
from . import views

app_name = 'zoekApp'
urlpatterns = [
    path('', views.zoek, name='zoek'),
    path("bestellingen/", views.bestellingen, name="bestellingen"),
    #path("bestellingen/bestellingen_resultaten", views.bestellingen_resultaten, name="Bestellingen_resultaten"),
    path("producten/", views.producten, name="producten"),
    path("alles/", views.alles, name="alles")
]