# reviews/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review
from .forms import ReviewForm
from products.models import Product
from orders.models import Order


@login_required
def ajouter_avis(request, slug):
    """Ajouter un avis sur un produit"""
    produit = get_object_or_404(Product, slug=slug)

    # Vérifier que l'utilisateur est acheteur
    if request.user.est_vendeur():
        messages.error(request, "Les vendeurs ne peuvent pas laisser d'avis.")
        return redirect('detail_produit', slug=slug)

    # Vérifier que l'utilisateur a acheté le produit
    a_achete = Order.objects.filter(
        acheteur=request.user,
        statut='livree',
        items__product=produit
    ).exists()

    if not a_achete:
        messages.warning(request, "Vous devez avoir acheté et reçu ce produit pour laisser un avis.")
        return redirect('detail_produit', slug=slug)

    # Vérifier si avis déjà existant
    avis_existant = Review.objects.filter(
        produit=produit,
        auteur=request.user
    ).first()

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=avis_existant)
        if form.is_valid():
            avis = form.save(commit=False)
            avis.produit = produit
            avis.auteur = request.user
            avis.save()
            messages.success(request, "Votre avis a été publié avec succès !")
            return redirect('detail_produit', slug=slug)
    else:
        form = ReviewForm(instance=avis_existant)

    context = {
        'form': form,
        'produit': produit,
        'avis_existant': avis_existant,
    }
    return render(request, 'reviews/ajouter_avis.html', context)


@login_required
def supprimer_avis(request, review_id):
    """Supprimer un avis"""
    avis = get_object_or_404(Review, id=review_id, auteur=request.user)
    slug = avis.produit.slug
    avis.delete()
    messages.success(request, "Votre avis a été supprimé.")
    return redirect('detail_produit', slug=slug)


def liste_avis_produit(request, slug):
    """Tous les avis d'un produit"""
    produit = get_object_or_404(Product, slug=slug)
    avis = Review.objects.filter(
        produit=produit
    ).select_related('auteur').order_by('-created_at')

    # Calcul moyenne
    if avis.exists():
        moyenne = sum(a.note for a in avis) / avis.count()
    else:
        moyenne = 0

    context = {
        'produit': produit,
        'avis': avis,
        'moyenne': round(moyenne, 1),
        'total': avis.count(),
    }
    return render(request, 'reviews/liste_avis.html', context)