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

    path(
        '<slug:slug>/',
        views.crop_problem_detail,
        name='crop_problem_detail'
    ),

]
