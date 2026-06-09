from django.urls import path
from . import views

urlpatterns = [

    path(
        '',
        views.products,
        name='products'
    ),

    path(
        '<int:id>/',
        views.product_detail,
        name='product_detail'
    ),

    path(
        'cart/',
        views.cart,
        name='cart'
    ),

    path(
        'add-to-cart/<int:id>/',
        views.add_to_cart,
        name='add_to_cart'
    ),

    path(
        'remove-from-cart/<int:id>/',
        views.remove_from_cart,
        name='remove_from_cart'
    ),

]