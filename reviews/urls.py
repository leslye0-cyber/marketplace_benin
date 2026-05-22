# reviews/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('avis/<slug:slug>/ajouter/', views.ajouter_avis, name='ajouter_avis'),
    path('avis/<int:review_id>/supprimer/', views.supprimer_avis, name='supprimer_avis'),
    path('avis/<slug:slug>/tous/', views.liste_avis_produit, name='liste_avis_produit'),
]