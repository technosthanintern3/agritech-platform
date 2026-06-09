from django.contrib import admin
from .models import Machinery, TractorBooking


@admin.register(Machinery)
class MachineryAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'price_per_day'
    )

    search_fields = (
        'name',
    )


@admin.register(TractorBooking)
class TractorBookingAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'machinery_type',
        'booking_date',
        'created_at'
    )

    list_filter = (
        'machinery_type',
        'booking_date'
    )

    search_fields = (
        'name',
        'email',
        'phone'
    )