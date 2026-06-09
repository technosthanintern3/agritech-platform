from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import SeedVariety, Review
from .forms import ReviewForm
from django.db.models import Q, Avg
from agritech.utils import login_required_session


def products(request):

    query = request.GET.get('q')

    if query:

        seeds = SeedVariety.objects.filter(
            Q(name__icontains=query) |
            Q(crop__name__icontains=query) |
            Q(season__icontains=query) |
            Q(soil_type__icontains=query)
        )

    else:

        seeds = SeedVariety.objects.all()

    cart = request.session.get(
        'cart',
        {}
    )

    cart_ids = [str(key) for key in cart.keys()]

    return render(
        request,
        'products/products.html',
        {
            'seeds': seeds,
            'cart': cart,
            'cart_ids': cart_ids
        }
    )


def product_detail(request, id):

    seed = get_object_or_404(
        SeedVariety,
        id=id
    )

    reviews = Review.objects.filter(
        product=seed
    ).order_by(
        '-created_at'
    )
    
    average_rating = reviews.aggregate(
        Avg('rating')
    )['rating__avg']

    # IMPORTANT: Always create form first
    form = ReviewForm()

    if request.method == 'POST':

        form = ReviewForm(request.POST)

        if form.is_valid():

            review = form.save(
                commit=False
            )

            review.product = seed

            review.save()

            return redirect(
                'product_detail',
                id=seed.id
            )

    cart = request.session.get(
        'cart',
        {}
    )

    return render(
        request,
        'products/product_detail.html',
        {
            'seed': seed,
            'reviews': reviews,
            'form': form,
            'cart': cart,
            'average_rating': average_rating
        }
    )


def add_to_cart(request, id):

    quantity = int(
        request.POST.get(
            'quantity',
            1
        )
    )

    cart = request.session.get(
        'cart',
        {}
    )

    if str(id) in cart:

        cart[str(id)] += quantity

    else:

        cart[str(id)] = quantity

    request.session['cart'] = cart
    request.session.modified = True

    return redirect(
        request.META.get(
            'HTTP_REFERER',
            'products'
        )
    )


def cart(request):

    cart = request.session.get(
        'cart',
        {}
    )

    items = []

    total = 0

    for product_id, quantity in cart.items():

        seed = SeedVariety.objects.get(
            id=product_id
        )

        subtotal = seed.price * quantity

        total += subtotal

        items.append({

            'seed': seed,
            'quantity': quantity,
            'subtotal': subtotal

        })

    return render(
        request,
        'products/cart.html',
        {
            'items': items,
            'total': total
        }
    )


def remove_from_cart(request, id):

    cart = request.session.get(
        'cart',
        {}
    )

    if str(id) in cart:

        del cart[str(id)]

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')
@login_required_session
def add_to_cart(request, id):

    quantity = int(
        request.POST.get(
            'quantity',
            1
        )
    )

    cart = request.session.get(
        'cart',
        {}
    )

    if str(id) in cart:

        cart[str(id)] += quantity

    else:

        cart[str(id)] = quantity

    request.session['cart'] = cart

    request.session.modified = True

    return redirect(
        request.META.get(
            'HTTP_REFERER',
            'products'
        )
    )