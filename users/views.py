# users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .forms import InscriptionAcheteurForm, InscriptionVendeurForm, ConnexionForm, ProfilForm
from orders.models import Order, OrderItem


def inscription_acheteur(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = InscriptionAcheteurForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Bienvenue {user.username} !")
            return redirect('home')
    else:
        form = InscriptionAcheteurForm()
    return render(request, 'users/inscription_acheteur.html', {'form': form})


def inscription_vendeur(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = InscriptionVendeurForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Bienvenue {user.username} ! Votre boutique a été créée.")
            return redirect('dashboard_vendeur')
    else:
        form = InscriptionVendeurForm()
    return render(request, 'users/inscription_vendeur.html', {'form': form})


def connexion(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = ConnexionForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bienvenue {user.username} !")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            if user.est_vendeur():
                return redirect('dashboard_vendeur')
            return redirect('home')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = ConnexionForm(request)
    return render(request, 'users/connexion.html', {'form': form})


@login_required
def deconnexion(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('connexion')


@login_required
def profil(request):
    if request.method == 'POST':
        form = ProfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('profil')
    else:
        form = ProfilForm(instance=request.user)
    return render(request, 'users/profil.html', {'form': form})


@login_required
def dashboard_vendeur(request):
    if not request.user.est_vendeur():
        messages.error(request, "Accès réservé aux vendeurs.")
        return redirect('home')

    shop = request.user.shop
    produits = shop.products.all()

    aujourd_hui = timezone.now()
    debut_mois = aujourd_hui.replace(day=1, hour=0, minute=0, second=0)
    debut_semaine = aujourd_hui - timedelta(days=7)

    commandes_ids = OrderItem.objects.filter(
        product__shop=shop
    ).values_list('order_id', flat=True).distinct()

    commandes = Order.objects.filter(
        id__in=commandes_ids
    ).exclude(statut='panier').order_by('-created_at')

    commandes_recentes = commandes[:5]
    total_commandes = commandes.count()
    commandes_en_attente = commandes.filter(statut='en_attente').count()
    commandes_payees = commandes.filter(
        statut__in=['payee', 'en_preparation', 'expediee', 'livree']
    ).count()
    commandes_livrees = commandes.filter(statut='livree').count()

    items_vendeur = OrderItem.objects.filter(
        product__shop=shop,
        order__statut__in=['payee', 'en_preparation', 'expediee', 'livree']
    )

    revenu_total = sum(item.get_total() for item in items_vendeur) or Decimal('0')
    items_mois = items_vendeur.filter(order__created_at__gte=debut_mois)
    revenu_mois = sum(item.get_total() for item in items_mois) or Decimal('0')
    items_semaine = items_vendeur.filter(order__created_at__gte=debut_semaine)
    revenu_semaine = sum(item.get_total() for item in items_semaine) or Decimal('0')

    commission_total = int(revenu_total * Decimal('0.05'))
    revenu_net = int(revenu_total * Decimal('0.95'))

    produits_populaires = OrderItem.objects.filter(
        product__shop=shop,
        order__statut__in=['payee', 'en_preparation', 'expediee', 'livree']
    ).values(
        'product__nom', 'product__slug', 'product__prix'
    ).annotate(
        total_vendu=Sum('quantite'),
        total_revenu=Sum('prix_unitaire')
    ).order_by('-total_vendu')[:5]

    stock_critique = produits.filter(stock__lte=3, statut='disponible')

    context = {
        'shop': shop,
        'produits': produits,
        'total_produits': produits.count(),
        'commandes_recentes': commandes_recentes,
        'total_commandes': total_commandes,
        'commandes_en_attente': commandes_en_attente,
        'commandes_payees': commandes_payees,
        'commandes_livrees': commandes_livrees,
        'revenu_total': revenu_total,
        'revenu_mois': revenu_mois,
        'revenu_semaine': revenu_semaine,
        'commission_total': commission_total,
        'revenu_net': revenu_net,
        'produits_populaires': produits_populaires,
        'stock_critique': stock_critique,
    }
    return render(request, 'users/dashboard_vendeur.html', context)


@login_required
def commandes_vendeur(request):
    if not request.user.est_vendeur():
        return redirect('home')

    shop = request.user.shop
    statut = request.GET.get('statut', '')

    commandes_ids = OrderItem.objects.filter(
        product__shop=shop
    ).values_list('order_id', flat=True).distinct()

    commandes = Order.objects.filter(
        id__in=commandes_ids
    ).exclude(statut='panier').order_by('-created_at')

    if statut:
        commandes = commandes.filter(statut=statut)

    context = {
        'commandes': commandes,
        'statut_filtre': statut,
        'shop': shop,
    }
    return render(request, 'users/commandes_vendeur.html', context)


@login_required
def stats_admin(request):
    if not request.user.is_staff:
        return redirect('home')

    from products.models import Product
    from users.models import Shop, CustomUser

    total_users = CustomUser.objects.filter(role='acheteur').count()
    total_vendeurs = CustomUser.objects.filter(role='vendeur').count()
    total_boutiques = Shop.objects.filter(statut='actif').count()
    total_produits = Product.objects.filter(statut='disponible').count()

    total_commandes = Order.objects.exclude(statut='panier').count()
    commandes_payees = Order.objects.filter(
        statut__in=['payee', 'en_preparation', 'expediee', 'livree']
    ).count()

    revenus_bruts = sum(
        o.total for o in Order.objects.filter(
            statut__in=['payee', 'en_preparation', 'expediee', 'livree']
        )
    ) or Decimal('0')

    commissions_totales = int(revenus_bruts * Decimal('0.05'))

    from users.models import CustomUser as User
    vendeurs_recents = User.objects.filter(
        role='vendeur'
    ).order_by('-date_joined')[:5]

    commandes_recentes = Order.objects.exclude(
        statut='panier'
    ).order_by('-created_at')[:10]

    context = {
        'total_users': total_users,
        'total_vendeurs': total_vendeurs,
        'total_boutiques': total_boutiques,
        'total_produits': total_produits,
        'total_commandes': total_commandes,
        'commandes_payees': commandes_payees,
        'revenus_bruts': revenus_bruts,
        'commissions_totales': commissions_totales,
        'vendeurs_recents': vendeurs_recents,
        'commandes_recentes': commandes_recentes,
    }
    return render(request, 'users/stats_admin.html', context)