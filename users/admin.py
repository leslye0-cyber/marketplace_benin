# users/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Shop


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'telephone', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'telephone']
    fieldsets = UserAdmin.fieldsets + (
        ('Infos supplémentaires', {
            'fields': ('role', 'telephone', 'adresse', 'photo')
        }),
    )
    actions = ['activer_comptes', 'desactiver_comptes']

    def activer_comptes(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} compte(s) activé(s).")
    activer_comptes.short_description = "✅ Activer les comptes"

    def desactiver_comptes(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} compte(s) désactivé(s).")
    desactiver_comptes.short_description = "❌ Désactiver les comptes"


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['nom', 'vendeur', 'statut', 'est_premium', 'created_at']
    list_filter = ['statut', 'est_premium']
    search_fields = ['nom', 'vendeur__username']
    actions = ['activer_boutiques', 'suspendre_boutiques', 'activer_premium']

    def activer_boutiques(self, request, queryset):
        queryset.update(statut='actif')
        self.message_user(request, f"{queryset.count()} boutique(s) activée(s).")
    activer_boutiques.short_description = "✅ Activer les boutiques"

    def suspendre_boutiques(self, request, queryset):
        queryset.update(statut='suspendu')
        self.message_user(request, f"{queryset.count()} boutique(s) suspendue(s).")
    suspendre_boutiques.short_description = "🚫 Suspendre les boutiques"

    def activer_premium(self, request, queryset):
        queryset.update(est_premium=True)
        self.message_user(request, f"{queryset.count()} boutique(s) passée(s) en premium.")
    activer_premium.short_description = "⭐ Passer en Premium"