# users/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Shop


class InscriptionAcheteurForm(UserCreationForm):
    email = forms.EmailField(required=True)
    telephone = forms.CharField(max_length=20, required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'telephone', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.telephone = self.cleaned_data['telephone']
        user.role = 'acheteur'
        if commit:
            user.save()
        return user


class InscriptionVendeurForm(UserCreationForm):
    email = forms.EmailField(required=True)
    telephone = forms.CharField(max_length=20, required=True)
    adresse = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)

    # Infos boutique
    nom_shop = forms.CharField(max_length=100, label="Nom de votre boutique")
    description_shop = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        label="Description de la boutique",
        required=False
    )

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'telephone',
            'adresse', 'password1', 'password2',
            'nom_shop', 'description_shop'
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.telephone = self.cleaned_data['telephone']
        user.adresse = self.cleaned_data['adresse']
        user.role = 'vendeur'
        if commit:
            user.save()
            # Créer automatiquement la boutique
            Shop.objects.create(
                vendeur=user,
                nom=self.cleaned_data['nom_shop'],
                description=self.cleaned_data['description_shop'],
            )
        return user


class ConnexionForm(AuthenticationForm):
    username = forms.CharField(label="Nom d'utilisateur")
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)


class ProfilForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'telephone', 'adresse', 'photo']
        widgets = {
            'adresse': forms.Textarea(attrs={'rows': 2}),
        }