from django.urls import path
from . import views

app_name = 'nieuwApp'
urlpatterns = [
    path('', views.nieuw, name='nieuw'),
    path('bestelling', views.nieuw_bestel, name='nieuwbestelling'),
    path('product', views.nieuw_keuze, name='nieuwproduct'),
    path('done', views.bestel_done, name='besteldone'),
    path('producttoevoegen', views.prod_toevoegen, name='producttoevoegen'),
    path('specialeoptie', views.speciale_optie, name='specialeoptie'),
]
