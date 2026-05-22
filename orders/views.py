# orders/views.py

import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem
from .forms import CommandeForm, PaiementMobileMoneyForm
from products.models import Product


@login_required
def ajouter_au_panier(request, product_id):
    produit = get_object_or_404(Product, id=product_id, statut='disponible')

    if request.user.est_vendeur():
        messages.error(request, "Les vendeurs ne peuvent pas acheter.")
        return redirect('detail_produit', slug=produit.slug)

    panier, created = Order.objects.get_or_create(
        acheteur=request.user,
        statut='panier'
    )

    quantite = int(request.POST.get('quantite', 1))

    if quantite > produit.stock:
        messages.error(request, f"Stock insuffisant. Seulement {produit.stock} disponibles.")
        return redirect('detail_produit', slug=produit.slug)

    item, item_created = OrderItem.objects.get_or_create(
        order=panier,
        product=produit,
        defaults={'prix_unitaire': produit.prix, 'quantite': quantite}
    )

    if not item_created:
        item.quantite += quantite
        item.save()

    panier.calculer_total()
    messages.success(request, f"'{produit.nom}' ajouté au panier !")
    return redirect('voir_panier')


@login_required
def voir_panier(request):
    try:
        panier = Order.objects.get(acheteur=request.user, statut='panier')
        items = panier.items.all().select_related('product')
        panier.calculer_total()
    except Order.DoesNotExist:
        panier = None
        items = []

    context = {
        'panier': panier,
        'items': items,
    }
    return render(request, 'orders/panier.html', context)


@login_required
def modifier_quantite(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__acheteur=request.user)
    action = request.POST.get('action')

    if action == 'augmenter':
        if item.quantite < item.product.stock:
            item.quantite += 1
            item.save()
    elif action == 'diminuer':
        if item.quantite > 1:
            item.quantite -= 1
            item.save()
        else:
            item.delete()
            messages.info(request, "Article retiré du panier.")
            item.order.calculer_total()
            return redirect('voir_panier')

    item.order.calculer_total()
    return redirect('voir_panier')


@login_required
def supprimer_du_panier(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__acheteur=request.user)
    panier = item.order
    nom = item.product.nom
    item.delete()
    panier.calculer_total()
    messages.success(request, f"'{nom}' retiré du panier.")
    return redirect('voir_panier')


@login_required
def checkout(request):
    try:
        panier = Order.objects.get(acheteur=request.user, statut='panier')
    except Order.DoesNotExist:
        messages.error(request, "Votre panier est vide.")
        return redirect('home')

    if not panier.items.exists():
        messages.error(request, "Votre panier est vide.")
        return redirect('voir_panier')

    if request.method == 'POST':
        form = CommandeForm(request.POST, instance=panier)
        if form.is_valid():
            commande = form.save(commit=False)
            commande.frais_livraison = 1000
            commande.statut = 'en_attente'
            commande.calculer_total()
            commande.save()
            # Rediriger vers le paiement
            return redirect('paiement', order_id=commande.id)
    else:
        form = CommandeForm(instance=panier, initial={
            'telephone_livraison': request.user.telephone,
            'adresse_livraison': request.user.adresse,
        })

    panier.calculer_total()

    context = {
        'panier': panier,
        'items': panier.items.all().select_related('product'),
        'form': form,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def paiement(request, order_id):
    """Page de paiement Mobile Money"""
    commande = get_object_or_404(Order, id=order_id, acheteur=request.user)

    # Si déjà payée
    if commande.paiement_confirme:
        return redirect('confirmation_commande', order_id=commande.id)

    # Si espèces → confirmation directe
    if commande.methode_paiement == 'especes':
        commande.statut = 'en_preparation'
        commande.paiement_confirme = False
        commande.reference_paiement = f"ESP-{uuid.uuid4().hex[:8].upper()}"
        commande.save()
        messages.success(request, "Commande confirmée ! Paiement à la livraison.")
        return redirect('confirmation_commande', order_id=commande.id)

    if request.method == 'POST':
        form = PaiementMobileMoneyForm(request.POST)
        if form.is_valid():
            numero = form.cleaned_data['numero_mobile_money']
            commande.numero_paiement = numero
            commande.reference_paiement = f"REF-{uuid.uuid4().hex[:8].upper()}"
            commande.save()
            return redirect('confirmer_paiement', order_id=commande.id)
    else:
        form = PaiementMobileMoneyForm(initial={
            'numero_mobile_money': request.user.telephone
        })

    # Icône selon opérateur
    operateur = 'MTN' if commande.methode_paiement == 'mtn_momo' else 'Moov'
    couleur = '#FFCC00' if commande.methode_paiement == 'mtn_momo' else '#0066CC'

    context = {
        'commande': commande,
        'form': form,
        'operateur': operateur,
        'couleur': couleur,
    }
    return render(request, 'orders/paiement.html', context)


@login_required
def confirmer_paiement(request, order_id):
    """Page de confirmation du paiement — simulation"""
    commande = get_object_or_404(Order, id=order_id, acheteur=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'confirmer':
            # Simuler la confirmation du paiement
            commande.paiement_confirme = True
            commande.statut = 'payee'
            commande.save()

            # Mettre à jour le stock des produits
            for item in commande.items.all():
                produit = item.product
                produit.stock -= item.quantite
                if produit.stock <= 0:
                    produit.stock = 0
                    produit.statut = 'rupture'
                produit.save()

            messages.success(request, "Paiement confirmé ! Votre commande est en cours de traitement.")
            return redirect('confirmation_commande', order_id=commande.id)

        elif action == 'annuler':
            commande.statut = 'annulee'
            commande.save()
            messages.error(request, "Paiement annulé.")
            return redirect('mes_commandes')

    context = {
        'commande': commande,
    }
    return render(request, 'orders/confirmer_paiement.html', context)


@login_required
def confirmation_commande(request, order_id):
    commande = get_object_or_404(Order, id=order_id, acheteur=request.user)
    items = commande.items.all().select_related('product')

    context = {
        'commande': commande,
        'items': items,
    }
    return render(request, 'orders/confirmation.html', context)


@login_required
def mes_commandes(request):
    commandes = Order.objects.filter(
        acheteur=request.user
    ).exclude(statut='panier').order_by('-created_at')

    return render(request, 'orders/mes_commandes.html', {'commandes': commandes})


@login_required
def detail_commande(request, order_id):
    commande = get_object_or_404(Order, id=order_id, acheteur=request.user)
    items = commande.items.all().select_related('product')

    context = {
        'commande': commande,
        'items': items,
    }
    return render(request, 'orders/detail_commande.html', context)