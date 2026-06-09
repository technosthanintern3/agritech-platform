from django.urls import path
from .views import (
    consultation,
    my_consultations
)

urlpatterns = [

    path(
        '',
        consultation,
        name='consultation'
    ),

    path(
        'my-consultations/',
        my_consultations,
        name='my_consultations'
    ),

]