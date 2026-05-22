# users/urls.py

from django.urls import path
from . import views

urlpatterns = [ path('stats/', views.stats_admin, name='stats_admin'),
    path('inscription/acheteur/', views.inscription_acheteur, name='inscription_acheteur'),
    path('inscription/vendeur/', views.inscription_vendeur, name='inscription_vendeur'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('profil/', views.profil, name='profil'),
    path('dashboard/', views.dashboard_vendeur, name='dashboard_vendeur'),
    path('dashboard/commandes/', views.commandes_vendeur, name='commandes_vendeur'),
]