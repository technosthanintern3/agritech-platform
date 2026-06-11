from django.urls import path

from .views import (
    register,
    login_view,
    dashboard,
    logout_view,
    edit_profile,
    change_password
)

urlpatterns = [

    path(
        'register/',
        register,
        name='register'
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