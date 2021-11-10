from django.urls import path
from . import views

app_name = 'zoekApp'
urlpatterns = [
    path('', views.zoek, name='zoek'),
    path("bestellingen/", views.bestellingen, name="Bestellingen"),
    path("bestellingen/bestellingen_resultaten", views.bestellingen_resultaten, name="Bestellingen resultaten"),
    path("producten/", views.producten, name="Bestellingen")
]