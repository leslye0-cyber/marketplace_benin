# delivery/admin.py

from django.contrib import admin
from .models import Livraison, Livreur
from django.utils import timezone


@admin.register(Livreur)
class LivreurAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'vehicule', 'zone_couverture', 'est_disponible']
    list_filter = ['est_disponible']


@admin.register(Livraison)
class LivraisonAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'livreur', 'statut', 'created_at']
    list_filter = ['statut']
    search_fields = ['order__acheteur__username']
    actions = ['assigner_livraison']

    def save_model(self, request, obj, form, change):
        if obj.livreur and obj.statut == 'en_attente':
            obj.statut = 'assignee'
            obj.date_assignation = timezone.now()
        super().save_model(request, obj, form, change)
        # Mettre à jour le statut de la commande
        if obj.statut == 'assignee':
            obj.order.statut = 'en_preparation'
            obj.order.save()