from django.contrib import admin
from .models import Farmer, SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):

    fields = (
        'site_name',
        'logo',
        'hero_background',
        'mobile_hero_background',
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        form.base_fields['site_name'].required = False
        form.base_fields['logo'].required = False
        form.base_fields['hero_background'].required = False
        form.base_fields['mobile_hero_background'].required = False

        return form


admin.site.register(Farmer)