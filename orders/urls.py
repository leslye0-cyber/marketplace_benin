# orders/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('panier/', views.voir_panier, name='voir_panier'),
    path('ajouter/<int:product_id>/', views.ajouter_au_panier, name='ajouter_au_panier'),
    path('modifier/<int:item_id>/', views.modifier_quantite, name='modifier_quantite'),
    path('supprimer/<int:item_id>/', views.supprimer_du_panier, name='supprimer_du_panier'),
    path('checkout/', views.checkout, name='checkout'),
    path('paiement/<int:order_id>/', views.paiement, name='paiement'),
    path('confirmer-paiement/<int:order_id>/', views.confirmer_paiement, name='confirmer_paiement'),
    path('confirmation/<int:order_id>/', views.confirmation_commande, name='confirmation_commande'),
    path('mes-commandes/', views.mes_commandes, name='mes_commandes'),
    path('commande/<int:order_id>/', views.detail_commande, name='detail_commande'),
]