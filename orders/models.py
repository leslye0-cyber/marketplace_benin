# orders/models.py

from django.db import models
from users.models import CustomUser
from products.models import Product


class Order(models.Model):

    STATUT_CHOICES = (
        ('panier', 'Panier'),
        ('en_attente', 'En attente de paiement'),
        ('payee', 'Payée'),
        ('en_preparation', 'En préparation'),
        ('expediee', 'Expédiée'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
    )

    PAIEMENT_CHOICES = (
        ('mtn_momo', 'MTN Mobile Money'),
        ('moov_money', 'Moov Money'),
        ('especes', 'Espèces à la livraison'),
    )

    acheteur = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='panier')
    methode_paiement = models.CharField(max_length=20, choices=PAIEMENT_CHOICES, blank=True)
    adresse_livraison = models.TextField(blank=True)
    telephone_livraison = models.CharField(max_length=20, blank=True)
    ville = models.CharField(max_length=100, blank=True)
    sous_total = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    frais_livraison = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    numero_paiement = models.CharField(max_length=20, blank=True)
    reference_paiement = models.CharField(max_length=100, blank=True)
    paiement_confirme = models.BooleanField(default=False)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Commande #{self.id} — {self.acheteur.username}"

    def calculer_total(self):
        self.sous_total = sum(item.get_total() for item in self.items.all())
        self.total = self.sous_total + self.frais_livraison
        self.save()

    class Meta:
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'
        ordering = ['-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=0)

    def get_total(self):
        return self.prix_unitaire * self.quantite

    def __str__(self):
        return f"{self.quantite}x {self.product.nom}"

    class Meta:
        verbose_name = 'Article commandé'
        verbose_name_plural = 'Articles commandés'


class Commission(models.Model):
    """Commission prélevée par la plateforme sur chaque commande"""

    STATUT_CHOICES = (
        ('en_attente', 'En attente'),
        ('payee', 'Payée'),
    )

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='commission'
    )
    montant_total = models.DecimalField(max_digits=10, decimal_places=0)
    taux = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    montant_commission = models.DecimalField(max_digits=10, decimal_places=0)
    montant_vendeur = models.DecimalField(max_digits=10, decimal_places=0)
    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default='en_attente')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commission #{self.order.id} — {self.montant_commission} FCFA"

    class Meta:
        verbose_name = 'Commission'
        verbose_name_plural = 'Commissions'