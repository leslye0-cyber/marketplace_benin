# products/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from .models import Product, Categorie
from .forms import ProductForm, RechercheForm


def home(request):
    produits = Product.objects.filter(
        statut='disponible'
    ).select_related('shop', 'categorie')
    categories = Categorie.objects.all()
    form = RechercheForm(request.GET)

    q = request.GET.get('q', '')
    categorie_id = request.GET.get('categorie', '')
    prix_min = request.GET.get('prix_min', '')
    prix_max = request.GET.get('prix_max', '')

    if q:
        produits = produits.filter(nom__icontains=q)
    if categorie_id:
        produits = produits.filter(categorie__id=categorie_id)
    if prix_min:
        produits = produits.filter(prix__gte=prix_min)
    if prix_max:
        produits = produits.filter(prix__lte=prix_max)

    produits_vedette = produits.filter(est_mis_en_avant=True)[:4]

    context = {
        'produits': produits,
        'categories': categories,
        'form': form,
        'produits_vedette': produits_vedette,
        'recherche': q,
    }
    return render(request, 'products/home.html', context)


def detail_produit(request, slug):
    produit = get_object_or_404(Product, slug=slug, statut='disponible')
    images = produit.images.all()
    reviews = produit.reviews.all().select_related('auteur')
    produits_similaires = Product.objects.filter(
        categorie=produit.categorie,
        statut='disponible'
    ).exclude(id=produit.id)[:4]

    context = {
        'produit': produit,
        'images': images,
        'reviews': reviews,
        'produits_similaires': produits_similaires,
    }
    return render(request, 'products/detail_produit.html', context)


def produits_par_categorie(request, slug):
    categorie = get_object_or_404(Categorie, slug=slug)
    produits = Product.objects.filter(
        categorie=categorie,
        statut='disponible'
    ).select_related('shop')

    context = {
        'categorie': categorie,
        'produits': produits,
    }
    return render(request, 'products/categorie.html', context)


@login_required
def ajouter_produit(request):
    if not request.user.est_vendeur():
        messages.error(request, "Accès réservé aux vendeurs.")
        return redirect('home')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            produit = form.save(commit=False)
            produit.shop = request.user.shop
            base_slug = slugify(produit.nom)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            produit.slug = slug
            produit.save()
            messages.success(request, f"Produit '{produit.nom}' ajouté avec succès !")
            return redirect('dashboard_vendeur')
    else:
        form = ProductForm()

    return render(request, 'products/ajouter_produit.html', {'form': form})


@login_required
def modifier_produit(request, slug):
    produit = get_object_or_404(Product, slug=slug)

    if produit.shop.vendeur != request.user:
        messages.error(request, "Vous n'êtes pas autorisé à modifier ce produit.")
        return redirect('home')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=produit)
        if form.is_valid():
            form.save()
            messages.success(request, "Produit modifié avec succès !")
            return redirect('dashboard_vendeur')
    else:
        form = ProductForm(instance=produit)

    return render(request, 'products/modifier_produit.html', {
        'form': form,
        'produit': produit
    })


@login_required
def supprimer_produit(request, slug):
    produit = get_object_or_404(Product, slug=slug)

    if produit.shop.vendeur != request.user:
        messages.error(request, "Vous n'êtes pas autorisé à supprimer ce produit.")
        return redirect('home')

    if request.method == 'POST':
        nom = produit.nom
        produit.delete()
        messages.success(request, f"Produit '{nom}' supprimé.")
        return redirect('dashboard_vendeur')

    return render(request, 'products/confirmer_suppression.html', {'produit': produit})