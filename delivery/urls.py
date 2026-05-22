# delivery/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('mes-livraisons/', views.liste_livraisons, name='liste_livraisons'),
    path('livraison/<int:livraison_id>/', views.detail_livraison, name='detail_livraison'),
    path('livraison/<int:livraison_id>/statut/', views.mettre_a_jour_statut, name='mettre_a_jour_statut'),
    path('suivi/<int:order_id>/', views.suivi_livraison, name='suivi_livraison'),
]