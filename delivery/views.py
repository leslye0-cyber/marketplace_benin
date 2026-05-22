# delivery/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Livraison, Livreur
from orders.models import Order


@login_required
def liste_livraisons(request):
    """Liste des livraisons pour un livreur"""
    try:
        livreur = request.user.livreur
    except:
        messages.error(request, "Vous n'êtes pas enregistré comme livreur.")
        return redirect('home')

    livraisons = Livraison.objects.filter(
        livreur=livreur
    ).select_related('order__acheteur').order_by('-created_at')

    context = {
        'livraisons': livraisons,
        'livreur': livreur,
        'en_attente': livraisons.filter(statut='assignee').count(),
        'en_cours': livraisons.filter(statut='en_cours').count(),
        'livrees': livraisons.filter(statut='livree').count(),
    }
    return render(request, 'delivery/liste_livraisons.html', context)


@login_required
def detail_livraison(request, livraison_id):
    """Détail d'une livraison"""
    livraison = get_object_or_404(Livraison, id=livraison_id)

    # Vérifier accès — livreur ou acheteur concerné
    est_livreur = hasattr(request.user, 'livreur') and livraison.livreur == request.user.livreur
    est_acheteur = livraison.order.acheteur == request.user

    if not est_livreur and not est_acheteur and not request.user.is_staff:
        messages.error(request, "Accès non autorisé.")
        return redirect('home')

    context = {
        'livraison': livraison,
        'est_livreur': est_livreur,
    }
    return render(request, 'delivery/detail_livraison.html', context)


@login_required
def mettre_a_jour_statut(request, livraison_id):
    """Mettre à jour le statut d'une livraison"""
    livraison = get_object_or_404(Livraison, id=livraison_id)

    try:
        livreur = request.user.livreur
    except:
        messages.error(request, "Accès non autorisé.")
        return redirect('home')

    if livraison.livreur != livreur:
        messages.error(request, "Ce n'est pas votre livraison.")
        return redirect('liste_livraisons')

    if request.method == 'POST':
        nouveau_statut = request.POST.get('statut')
        statuts_valides = ['en_cours', 'livree', 'echouee']

        if nouveau_statut in statuts_valides:
            livraison.statut = nouveau_statut
            if nouveau_statut == 'livree':
                from django.utils import timezone
                livraison.date_livraison = timezone.now()
                livraison.order.statut = 'livree'
                livraison.order.save()
            elif nouveau_statut == 'en_cours':
                livraison.order.statut = 'expediee'
                livraison.order.save()
            livraison.save()
            messages.success(request, "Statut mis à jour avec succès.")

    return redirect('detail_livraison', livraison_id=livraison_id)


@login_required
def suivi_livraison(request, order_id):
    """Page de suivi pour l'acheteur"""
    commande = get_object_or_404(Order, id=order_id, acheteur=request.user)

    try:
        livraison = commande.livraison
    except:
        livraison = None

    context = {
        'commande': commande,
        'livraison': livraison,
    }
    return render(request, 'delivery/suivi_livraison.html', context)