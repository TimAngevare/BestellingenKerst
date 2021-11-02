from django.urls import path
from . import views

app_name = 'bestellingenApp'
urlpatterns = [
    path('', views.index, name='index'),
    path('zoeken', views.zoek, name='zoeken'),
    path('nieuw', views.nieuw, name='nieuw'),
    path('nieuwbestel', views.nieuw_bestel, name='nieuwbestel'),
    path('nieuwekeuze', views.nieuw_keuze, name='nieuwekeuze'),
]