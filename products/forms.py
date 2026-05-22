# products/forms.py

from django import forms
from .models import Product, Categorie


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'nom', 'categorie', 'description',
            'prix', 'stock', 'statut',
            'image_principale'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'prix': forms.NumberInput(attrs={'placeholder': 'Prix en FCFA'}),
            'stock': forms.NumberInput(attrs={'placeholder': 'Quantité disponible'}),
        }
        labels = {
            'nom': 'Nom du produit',
            'categorie': 'Catégorie',
            'description': 'Description',
            'prix': 'Prix (FCFA)',
            'stock': 'Stock disponible',
            'statut': 'Statut',
            'image_principale': 'Image principale',
        }


class RechercheForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Rechercher un produit...',
            'class': 'form-control'
        })
    )
    categorie = forms.ModelChoiceField(
        queryset=Categorie.objects.all(),
        required=False,
        empty_label="Toutes les catégories"
    )
    prix_min = forms.DecimalField(required=False, min_value=0)
    prix_max = forms.DecimalField(required=False, min_value=0)