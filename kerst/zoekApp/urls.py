from django.urls import path
from . import views

app_name = 'nieuwApp'
urlpatterns = [
    path('', views.zoek, name='zoek'),
    path("bestellingen/", views.bestellingen, name="Bestellingen"),
    path("producten/", views.producten, name="Bestellingen")
]