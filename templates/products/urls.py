from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('categorie/<slug:slug>/', views.produits_par_categorie, name='produits_par_categorie'),
    path('produit/ajouter/', views.ajouter_produit, name='ajouter_produit'),
    path('produit/<slug:slug>/', views.detail_produit, name='detail_produit'),
    path('produit/<slug:slug>/modifier/', views.modifier_produit, name='modifier_produit'),
    path('produit/<slug:slug>/supprimer/', views.supprimer_produit, name='supprimer_produit'),
]