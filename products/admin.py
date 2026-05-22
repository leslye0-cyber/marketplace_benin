# products/admin.py

from django.contrib import admin
from .models import Categorie, Product, ProductImage


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'slug']
    prepopulated_fields = {'slug': ('nom',)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['nom', 'shop', 'categorie', 'prix', 'stock', 'statut', 'est_mis_en_avant']
    list_filter = ['statut', 'categorie', 'est_mis_en_avant']
    search_fields = ['nom', 'description']
    prepopulated_fields = {'slug': ('nom',)}
    inlines = [ProductImageInline]
    actions = ['mettre_en_avant', 'retirer_mise_en_avant', 'marquer_rupture']

    def mettre_en_avant(self, request, queryset):
        queryset.update(est_mis_en_avant=True)
        self.message_user(request, f"{queryset.count()} produit(s) mis en avant.")
    mettre_en_avant.short_description = "⭐ Mettre en avant"

    def retirer_mise_en_avant(self, request, queryset):
        queryset.update(est_mis_en_avant=False)
        self.message_user(request, f"{queryset.count()} produit(s) retirés de la mise en avant.")
    retirer_mise_en_avant.short_description = "❌ Retirer de la mise en avant"

    def marquer_rupture(self, request, queryset):
        queryset.update(statut='rupture')
        self.message_user(request, f"{queryset.count()} produit(s) marqué(s) en rupture.")
    marquer_rupture.short_description = "⚠️ Marquer en rupture"