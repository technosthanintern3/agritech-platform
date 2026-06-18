from django.urls import path
from . import views

urlpatterns = [

    path(
        'login/',
        views.admin_login_view,
        name='admin_login'
    ),

    path(
        'logout/',
        views.admin_logout_view,
        name='admin_logout'
    ),

    path(
        '',
        views.admin_required(views.admin_dashboard),
        name='admin_dashboard'
    ),

    path(
        'farmers/',
        views.admin_required(views.farmers_list),
        name='farmers_list'
    ),
    path(
        "farmer/<int:pk>/",
        views.admin_required(views.farmer_details),
        name="farmer_details"
    ),

    path(
        'products/',
        views.admin_required(views.products_list),
        name='products_list'
    ),
    path(
        "products/add/",
        views.admin_required(views.add_product),
        name="add_product"
    ),
    path(
        "products/edit/<int:pk>/",
        views.admin_required(views.edit_product),
        name="edit_product"
    ),
    
    path(
        "products/delete/<int:pk>/",
        views.admin_required(views.delete_product),
        name="delete_product"
    ),

    path(
        'machinery/',
        views.admin_required(views.machinery_list),
        name='machinery_list'
    ),
    path(
        "machinery/add/",
        views.admin_required(views.add_machinery),
        name="add_machinery"
    ),
    path(
        "machinery/edit/<int:pk>/",
        views.admin_required(views.edit_machinery),
        name="edit_machinery"
    ),
    path(
        "machinery/delete/<int:pk>/",
        views.admin_required(views.delete_machinery),
        name="delete_machinery"
    ),

    path(
        'orders/',
        views.admin_required(views.orders_list),
        name='orders_list'
    ),
    path(
        "orders/update/<int:pk>/",
        views.admin_required(views.update_order_status),
        name="update_order_status"
    ),

    path(
        'services/',
        views.admin_required(views.services_list),
        name='services_list'
    ),
    path(
        "services/add/",
        views.admin_required(views.add_service),
        name="add_service"
    ),
    path(
        "services/edit/<int:pk>/",
        views.admin_required(views.edit_service),
        name="edit_service"
    ),
    path(
        "services/delete/<int:pk>/",
        views.admin_required(views.delete_service),
        name="delete_service"
    ),

    path(
        'consultations/',
        views.admin_required(views.consultations_list),
        name='consultations_list'
    ),
    path(
        "consultations/update/<int:pk>/",
        views.admin_required(views.update_consultation_status),
        name="update_consultation_status"
    ),

    path(
        'crop-problems/',
        views.admin_required(views.crop_problems_list),
        name='crop_problems_list'
    ),
    path(
        "crop-problems/reply/<int:pk>/",
        views.admin_required(views.reply_crop_problem),
        name="reply_crop_problem"
    ),

    path(
        'crops/',
        views.admin_required(views.crops_list),
        name='crops_list'
    ),
    path(
        "crops/add/ajax/",
        views.admin_required(views.add_crop_ajax),
        name="add_crop_ajax"
    ),
    
    path(
        "site-settings/",
        views.site_settings,
        name="site_settings"
    ),
    
    path(
        "why-choose-us/",
        views.why_choose_list,
        name="why_choose_list"
    ),
    path(
        "why-choose-us/add/",
        views.add_why_choose,
        name="add_why_choose"
    ),
    
    path(
        "footer-settings/",
        views.footer_settings,
        name="footer_settings"
    ),

    path(
        'doctors/',
        views.admin_required(views.doctors_management),
        name='doctors_management'
    ),

    path(
        'doctors/<int:pk>/<str:action>/',
        views.admin_required(views.doctor_action),
        name='doctor_action'
    ),

    path(
        'consultants/',
        views.admin_required(views.consultant_management),
        name='consultant_management'
    ),

    path(
        'consultants/<int:pk>/<str:action>/',
        views.admin_required(views.consultant_action),
        name='consultant_action'
    ),

]