# orders/admin.py

from django.contrib import admin
from django.db.models import Sum
from .models import Order, OrderItem, Commission
from decimal import Decimal


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['prix_unitaire', 'get_total']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'acheteur', 'statut', 'methode_paiement',
                    'total', 'paiement_confirme', 'created_at']
    list_filter = ['statut', 'methode_paiement', 'paiement_confirme']
    search_fields = ['acheteur__username', 'reference_paiement']
    readonly_fields = ['sous_total', 'total', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    actions = ['marquer_payee', 'marquer_en_preparation', 'marquer_livree', 'creer_commissions']

    def marquer_payee(self, request, queryset):
        queryset.update(statut='payee', paiement_confirme=True)
        self.message_user(request, f"{queryset.count()} commande(s) marquée(s) comme payée(s).")
    marquer_payee.short_description = "✅ Marquer comme payée"

    def marquer_en_preparation(self, request, queryset):
        queryset.update(statut='en_preparation')
        self.message_user(request, f"{queryset.count()} commande(s) en préparation.")
    marquer_en_preparation.short_description = "📦 Mettre en préparation"

    def marquer_livree(self, request, queryset):
        queryset.update(statut='livree')
        self.message_user(request, f"{queryset.count()} commande(s) marquée(s) comme livrée(s).")
    marquer_livree.short_description = "🚚 Marquer comme livrée"

    def creer_commissions(self, request, queryset):
        created = 0
        for order in queryset.filter(statut__in=['payee', 'en_preparation', 'expediee', 'livree']):
            if not hasattr(order, 'commission'):
                taux = Decimal('5.00')
                montant_commission = int(order.total * taux / 100)
                montant_vendeur = int(order.total - montant_commission)
                Commission.objects.create(
                    order=order,
                    montant_total=order.total,
                    taux=taux,
                    montant_commission=montant_commission,
                    montant_vendeur=montant_vendeur,
                )
                created += 1
        self.message_user(request, f"{created} commission(s) créée(s).")
    creer_commissions.short_description = "💰 Créer les commissions"


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ['order', 'montant_total', 'taux',
                    'montant_commission', 'montant_vendeur', 'statut', 'created_at']
    list_filter = ['statut']
    readonly_fields = ['order', 'montant_total', 'taux',
                       'montant_commission', 'montant_vendeur', 'created_at']
    actions = ['marquer_payee']

    def marquer_payee(self, request, queryset):
        queryset.update(statut='payee')
        self.message_user(request, f"{queryset.count()} commission(s) marquée(s) comme payée(s).")
    marquer_payee.short_description = "✅ Marquer commission payée"