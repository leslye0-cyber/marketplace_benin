# delivery/models.py

from django.db import models
from orders.models import Order
from users.models import CustomUser


class Livreur(models.Model):
    """Livreur partenaire"""

    utilisateur = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='livreur'
    )
    vehicule = models.CharField(max_length=50, blank=True)  # moto, vélo, voiture
    zone_couverture = models.CharField(max_length=200, blank=True)
    est_disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"Livreur : {self.utilisateur.username}"


class Livraison(models.Model):

    STATUT_CHOICES = (
        ('en_attente', 'En attente'),
        ('assignee', 'Assignée à un livreur'),
        ('en_cours', 'En cours de livraison'),
        ('livree', 'Livrée'),
        ('echouee', 'Échouée'),
    )

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='livraison'
    )
    livreur = models.ForeignKey(
        Livreur,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='livraisons'
    )

    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default='en_attente')
    adresse_depart = models.TextField()
    adresse_arrivee = models.TextField()

    date_assignation = models.DateTimeField(blank=True, null=True)
    date_livraison = models.DateTimeField(blank=True, null=True)

    numero_suivi = models.CharField(max_length=20, unique=True, blank=True, null=True)
    frais_livraison = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    note_livreur = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Livraison commande #{self.order.id}"

    class Meta:
        verbose_name = 'Livraison'
        verbose_name_plural = 'Livraisons'