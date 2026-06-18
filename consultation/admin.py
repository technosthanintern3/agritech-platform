from django.contrib import admin
from .models import ConsultationRequest



@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'email',
        'assigned_doctor',
        'assigned_consultant',
        'status',
        'created_at'
    )

    list_filter = (
        'status',
        'created_at'
    )