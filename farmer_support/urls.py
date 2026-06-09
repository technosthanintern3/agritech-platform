from django.urls import path
from . import views

urlpatterns = [

    path(
        '',
        views.farmer_support,
        name='farmer_support'
    ),

    path(
        'my-problems/',
        views.my_problems,
        name='my_problems'
    ),

]