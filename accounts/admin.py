from django.contrib import admin
from .models import Farmer, SiteSettings, Doctor, Consultant, Role, RolePageSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):

    fields = (

        # Basic Site Settings
        'site_name',
        'logo',

        # Hero Section
        'hero_background',
        'mobile_hero_background',
        'hero_video',

        # Why Choose Us
        'why_icon_1',
        'why_title_1',

        'why_icon_2',
        'why_title_2',

        'why_icon_3',
        'why_title_3',

        'why_icon_4',
        'why_title_4',

        # Footer
        'company_description',
        'footer_address',
        'footer_phone',
        'footer_email',

        'facebook',
        'instagram',
        'youtube',
        'linkedin',

        'copyright_text',
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):

    list_display = (
        'full_name',
        'email',
        'is_online',
        'last_seen',
        'is_approved',
        'is_active_status',
        'last_login_time',
        'registration_date'
    )

    list_filter = (
        'is_approved',
        'is_active_status',
    )


@admin.register(Consultant)
class ConsultantAdmin(admin.ModelAdmin):

    list_display = (
        'full_name',
        'email',
        'is_online',
        'last_seen',
        'is_approved',
        'is_active_status',
        'last_login_time',
        'registration_date'
    )

    list_filter = (
        'is_approved',
        'is_active_status',
    )


@admin.register(RolePageSettings)
class RolePageSettingsAdmin(admin.ModelAdmin):

    list_display = (
        'role_name',
        'slug',
        'updated_at',
    )

    search_fields = (
        'role_name',
        'slug',
    )

    fields = (
        'role_name',
        'slug',
        'farmer_title',
        'farmer_description',
        'farmer_icon',
        'doctor_title',
        'doctor_description',
        'doctor_icon',
        'consultant_title',
        'consultant_description',
        'consultant_icon',
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'slug',
        'register_url',
        'dashboard_url',
        'is_active',
    )

    list_filter = (
        'is_active',
    )

    search_fields = (
        'name',
        'slug',
    )

    prepopulated_fields = {
        'slug': ('name',)
    }


admin.site.register(Farmer)
