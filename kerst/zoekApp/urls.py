from django.urls import path
from django.conf.urls import url
from . import views

app_name = 'zoekApp'
urlpatterns = [
    path('', views.zoek, name='zoek'),
    path("bestellingen/", views.bestellingen, name="bestellingen"),
    #path("bestellingen/bestellingen_resultaten", views.bestellingen_resultaten, name="Bestellingen_resultaten"),
    path("producten/", views.producten, name="producten"),
    path("ales/", views.alles, name="alles"),
    url(r'^alles/$', views.alles_result, name='alles_result')
]