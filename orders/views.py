from django.shortcuts import render, redirect
from .forms import OrderForm
from .models import Order
from products.models import SeedVariety
from agritech.utils import login_required_session


@login_required_session
def checkout(request):

    cart = request.session.get('cart', {})

    if not cart:
        return redirect('cart')

    total = 0

    for product_id, quantity in cart.items():

        seed = SeedVariety.objects.get(id=product_id)

        total += seed.price * quantity

    if request.method == 'POST':

        form = OrderForm(request.POST)

        if form.is_valid():

            order = form.save(commit=False)

            order.farmer_id = request.session.get('farmer_id')
            order.total_amount = total

            order.save()

            request.session['cart'] = {}

            return render(
                request,
                'orders/success.html'
            )

    else:

        form = OrderForm()

    return render(
        request,
        'orders/checkout.html',
        {
            'form': form,
            'total': total
        }
    )


@login_required_session
def my_orders(request):

    farmer_id = request.session.get('farmer_id')

    orders = Order.objects.filter(
        farmer_id=farmer_id
    ).order_by('-created_at')

    return render(
        request,
        'orders/my_orders.html',
        {
            'orders': orders
        }
    )