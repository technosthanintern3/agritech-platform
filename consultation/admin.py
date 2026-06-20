from django.contrib import admin
from .models import ConsultationRequest, ConsultationTopic


@admin.register(ConsultationTopic)
class ConsultationTopicAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'slug',
        'is_active',
        'created_at'
    )

    list_filter = (
        'is_active',
        'created_at'
    )

    search_fields = (
        'title',
        'short_summary'
    )

    prepopulated_fields = {
        'slug': ('title',)
    }



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
