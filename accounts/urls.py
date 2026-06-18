from django.urls import path

from .views import (
    choose_role,
    register,
    login_view,
    dashboard,
    doctor_register,
    consultant_register,
    logout_view,
    edit_profile,
    change_password
)

urlpatterns = [

    path(
        'choose-role/',
        choose_role,
        name='choose_role'
    ),

    path(
        'register/',
        register,
        name='register'
    ),

    path(
        'doctor-register/',
        doctor_register,
        name='doctor_register'
    ),

    path(
        'consultant-register/',
        consultant_register,
        name='consultant_register'
    ),

    path(
        'login/',
        login_view,
        name='login'
    ),

    path(
        'dashboard/',
        dashboard,
        name='dashboard'
    ),

    path(
        'logout/',
        logout_view,
        name='logout'
    ),
    path(
    'edit-profile/',
    edit_profile,
    name='edit_profile'
    ),
    path(
    'change-password/',
    change_password,
    name='change_password'
    ),
]