from django.urls import path

from .views import (
    tractor_booking,
    my_bookings,
    machinery_detail
)

urlpatterns = [

    path(
        '',
        tractor_booking,
        name='tractor_booking'
    ),

    path(
        'my-bookings/',
        my_bookings,
        name='my_bookings'
    ),

    path(
        'detail/<int:id>/',
        machinery_detail,
        name='machinery_detail'
    ),

]