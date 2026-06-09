from django.shortcuts import render
from products.models import SeedVariety


def home(request):

    products = SeedVariety.objects.all()[:6]

    return render(
        request,
        'company/home.html',
        {
            'products': products
        }
    )


def about(request):
    return render(request, 'company/about.html')


def contact(request):
    return render(request, 'company/contact.html')