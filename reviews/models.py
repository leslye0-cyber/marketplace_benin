# reviews/models.py

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import CustomUser
from products.models import Product


class Review(models.Model):

    produit = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    auteur = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    note = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    commentaire = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('produit', 'auteur')
        verbose_name = 'Avis'
        verbose_name_plural = 'Avis'
        ordering = ['-created_at']

    def __str__(self):
        return f"Avis de {self.auteur.username} sur {self.produit.nom} ({self.note}★)"