# users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):

    ROLE_CHOICES = (
        ('acheteur', 'Acheteur'),
        ('vendeur', 'Vendeur'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='acheteur')
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.TextField(blank=True)
    photo = models.ImageField(upload_to='users/', blank=True, null=True)

    class Meta:
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return f"{self.username} ({self.role})"

    def est_vendeur(self):
        return self.role == 'vendeur'

    def est_acheteur(self):
        return self.role == 'acheteur'


class Shop(models.Model):

    STATUT_CHOICES = (
        ('actif', 'Actif'),
        ('inactif', 'Inactif'),
        ('suspendu', 'Suspendu'),
    )

    vendeur = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='shop'
    )
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='shops/logos/', blank=True, null=True)
    banniere = models.ImageField(upload_to='shops/bannieres/', blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.TextField(blank=True)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='actif')
    est_premium = models.BooleanField(default=False)
    date_expiration_premium = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = 'Boutique'
        verbose_name_plural = 'Boutiques'