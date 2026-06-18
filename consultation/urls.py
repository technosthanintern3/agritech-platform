from django.urls import path
from .views import (
    consultation,
    my_consultations,
    doctor_dashboard,
    consultant_dashboard,
    doctor_consultation_detail,
    consultant_consultation_detail,
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

    path(
        'doctor-dashboard/',
        doctor_dashboard,
        name='doctor_dashboard'
    ),

    path(
        'doctor-dashboard/request/<int:pk>/',
        doctor_consultation_detail,
        name='doctor_consultation_detail'
    ),

    path(
        'consultant-dashboard/',
        consultant_dashboard,
        name='consultant_dashboard'
    ),

    path(
        'consultant-dashboard/request/<int:pk>/',
        consultant_consultation_detail,
        name='consultant_consultation_detail'
    ),

]