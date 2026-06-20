from django.contrib import admin
from .models import CropProblem, AdminReply, CropProblemGuide


@admin.register(CropProblemGuide)
class CropProblemGuideAdmin(admin.ModelAdmin):

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

admin.site.register(CropProblem)
admin.site.register(AdminReply)
