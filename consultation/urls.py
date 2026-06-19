from django.urls import path
from .views import (
    consultation,
    my_consultations,
    doctor_dashboard,
    consultant_dashboard,
    doctor_consultation_detail,
    consultant_consultation_detail,
    update_doctor_availability,
    update_consultant_availability,
    doctor_status_toggle,
    consultant_status_toggle,
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
        'doctor-dashboard/availability/',
        update_doctor_availability,
        name='update_doctor_availability'
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

        path(
            'doctor-dashboard/status/',
            doctor_status_toggle,
            name='doctor_status_toggle'
        ),

        path(
            'consultant-dashboard/status/',
            consultant_status_toggle,
            name='consultant_status_toggle'
        ),

    path(
        'consultant-dashboard/availability/',
        update_consultant_availability,
        name='update_consultant_availability'
    ),

]
