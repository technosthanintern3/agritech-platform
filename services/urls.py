from django.urls import path
from . import views

urlpatterns = [

    path(
        '',
        views.services,
        name='services'
    ),

    path(
        'my-requests/',
        views.my_requests,
        name='my_requests'
    ),
    path(
    'info/<str:service_name>/',
    views.service_info,
    name='service_info'
    ),
    
    path(
        'machinery-details/',
        views.machinery_details,
        name='machinery_details'
    ),
      path(
        'farmer-support-details/',
        views.farmer_support_details,
        name='farmer_support_details'
    ),
      path(
        'service/<slug:service_name>/',
        views.service_info,
        name='service_info'
    ),

]