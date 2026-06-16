from django.contrib import admin
from .models import ServiceRequest
from .models import ServiceInfo

admin.site.register(ServiceRequest)

@admin.register(ServiceInfo)
class ServiceInfoAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'slug',
        'created_at'
    )

    prepopulated_fields = {
        'slug': ('title',)
    }