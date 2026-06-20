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
    change_password,
    doctor_profile,
    consultant_profile,
    request_doctor_identity_change,
    request_consultant_identity_change,
    admin_register,
    forgot_password,
    forgot_password_verify,
    forgot_password_reset,
    registration_verify,
    resend_registration_otp,
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
        {'role': None},
        name='register'
    ),

    path(
        'register/farmer/',
        register,
        {'role': 'farmer'},
        name='register_farmer'
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
        'admin-register/',
        admin_register,
        name='admin_register'
    ),
    path(
        'verify-registration/<uuid:token>/',
        registration_verify,
        name='registration_verify'
    ),
    path(
        'verify-registration/<uuid:token>/resend/',
        resend_registration_otp,
        name='resend_registration_otp'
    ),
    path(
        'forgot-password/',
        forgot_password,
        name='forgot_password'
    ),
    path(
        'forgot-password/verify/<uuid:token>/',
        forgot_password_verify,
        name='forgot_password_verify'
    ),
    path(
        'forgot-password/reset/',
        forgot_password_reset,
        name='forgot_password_reset'
    ),

    path(
        'login/',
        login_view,
        {'role': None},
        name='login'
    ),

    path(
        'login/farmer/',
        login_view,
        {'role': 'farmer'},
        name='login_farmer'
    ),

    path(
        'login/doctor/',
        login_view,
        {'role': 'doctor'},
        name='login_doctor'
    ),

    path(
        'login/consultant/',
        login_view,
        {'role': 'consultant'},
        name='login_consultant'
    ),

    path(
        'login/admin/',
        login_view,
        {'role': 'admin'},
        name='login_admin'
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
    path(
        'doctor-profile/',
        doctor_profile,
        name='doctor_profile'
    ),
    path(
        'consultant-profile/',
        consultant_profile,
        name='consultant_profile'
    ),
    path(
        'doctor-profile/request-identity-change/',
        request_doctor_identity_change,
        name='request_doctor_identity_change'
    ),
    path(
        'consultant-profile/request-identity-change/',
        request_consultant_identity_change,
        name='request_consultant_identity_change'
    ),
]