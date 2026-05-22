# reviews/admin.py

from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['produit', 'auteur', 'note', 'created_at']
    list_filter = ['note']
    search_fields = ['produit__nom', 'auteur__username']
    readonly_fields = ['created_at']