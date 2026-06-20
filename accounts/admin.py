from django.contrib import admin
from .models import (
    AdminProfile,
    Farmer,
    FooterSettings,
    RegistrationField,
    SiteSettings,
    Doctor,
    Consultant,
    Role,
    RolePageSettings,
    VerificationHistory,
    WhyChooseUs,
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):

    fields = (
        'site_name',
        'logo',
        'hero_background',
        'mobile_hero_background',
        'hero_video',
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()


@admin.register(FooterSettings)
class FooterSettingsAdmin(admin.ModelAdmin):

    fields = (
        'company_description',
        'address',
        'phone',
        'email',
        'facebook',
        'instagram',
        'youtube',
        'linkedin',
        'copyright_text',
    )

    def has_add_permission(self, request):
        return not FooterSettings.objects.exists()


@admin.register(WhyChooseUs)
class WhyChooseUsAdmin(admin.ModelAdmin):

    list_display = ('title', 'icon', 'created_at')
    search_fields = ('title',)


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):

    list_display = ('full_name', 'user', 'role', 'email_verified', 'phone_verified', 'created_at')
    list_filter = ('role', 'email_verified', 'phone_verified')
    search_fields = ('full_name', 'user__username', 'user__email')


@admin.register(RegistrationField)
class RegistrationFieldAdmin(admin.ModelAdmin):

    list_display = ('label', 'role', 'field_type', 'is_required', 'is_active', 'sort_order')
    list_filter = ('role', 'field_type', 'is_active', 'is_required')
    search_fields = ('label', 'key')


@admin.register(VerificationHistory)
class VerificationHistoryAdmin(admin.ModelAdmin):

    list_display = ('role', 'account_id', 'action', 'performed_by', 'created_at')
    list_filter = ('role', 'action')
    search_fields = ('account_id', 'note')
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
