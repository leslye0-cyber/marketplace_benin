# products/models.py

from django.db import models
from users.models import Shop


class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icone = models.CharField(max_length=50, blank=True)  # ex: "fa-tshirt"
    description = models.TextField(blank=True)

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'


class Product(models.Model):

    STATUT_CHOICES = (
        ('disponible', 'Disponible'),
        ('rupture', 'Rupture de stock'),
        ('inactif', 'Inactif'),
    )

    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name='products'
    )
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products'
    )

    nom = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    prix = models.DecimalField(max_digits=10, decimal_places=0)  # En FCFA
    stock = models.PositiveIntegerField(default=0)
    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default='disponible')

    # Mise en avant (pub interne)
    est_mis_en_avant = models.BooleanField(default=False)

    image_principale = models.ImageField(upload_to='products/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'
        ordering = ['-created_at']


class ProductImage(models.Model):
    """Images supplémentaires d'un produit"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='products/gallery/')
    ordre = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Image de {self.product.nom}"