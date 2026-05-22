# orders/forms.py

from django import forms
from .models import Order


class CommandeForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'adresse_livraison',
            'telephone_livraison',
            'ville',
            'methode_paiement',
            'note',
        ]
        widgets = {
            'adresse_livraison': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Ex: Quartier Akpakpa, Rue 12...'
            }),
            'telephone_livraison': forms.TextInput(attrs={
                'placeholder': 'Ex: 97000000'
            }),
            'ville': forms.TextInput(attrs={
                'placeholder': 'Ex: Cotonou, Porto-Novo...'
            }),
            'note': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Instructions spéciales...'
            }),
        }
        labels = {
            'adresse_livraison': 'Adresse de livraison',
            'telephone_livraison': 'Téléphone de livraison',
            'ville': 'Ville',
            'methode_paiement': 'Méthode de paiement',
            'note': 'Note (optionnel)',
        }


class PaiementMobileMoneyForm(forms.Form):
    numero_mobile_money = forms.CharField(
        max_length=20,
        label='Numéro Mobile Money',
        widget=forms.TextInput(attrs={
            'placeholder': 'Ex: 97000000',
            'class': 'form-control form-control-lg'
        })
    )

    def clean_numero_mobile_money(self):
        numero = self.cleaned_data['numero_mobile_money']
        # Nettoyer le numéro
        numero = numero.replace(' ', '').replace('-', '')
        # Vérifier que c'est un numéro béninois valide
        if not numero.isdigit():
            raise forms.ValidationError("Le numéro doit contenir uniquement des chiffres.")
        if len(numero) not in [8, 11]:
            raise forms.ValidationError("Numéro invalide. Ex: 97000000 ou 22997000000")
        return numero