from django import forms
from products.models import SeedVariety
from machinery.models import Machinery
from accounts.models import (
    SiteSettings,
    WhyChooseUs,
    FooterSettings,
    RolePageSettings
)
from django import forms


class ProductForm(forms.ModelForm):
    class Meta:
        model = SeedVariety
        fields = [
            'crop',
            'name',
            'image',
            'soil_type',
            'season',
            'water_requirement',
            'description',
            'price',
    ]

    widgets = {
        'description': forms.Textarea(
            attrs={'rows':4}
        )
    }

class MachineryForm(forms.ModelForm):

    class Meta:

        model = Machinery

        fields = [
            'name',
            'image',
            'description',
            'price_per_day'
        ]

        widgets = {

            'description': forms.Textarea(
                attrs={
                    'rows': 4
                }
            )

        }
        
class SiteSettingsForm(forms.ModelForm):

    class Meta:

        model = SiteSettings

        fields = [
            "site_name",
            "logo",
            "hero_background",
            "mobile_hero_background",
            "hero_video",
        ]
class WhyChooseUsForm(forms.ModelForm):

    class Meta:

        model = WhyChooseUs

        fields = [
            "icon",
            "title"
        ]
        
class FooterSettingsForm(forms.ModelForm):

    class Meta:

        model = FooterSettings

        fields = "__all__"


class RolePageSettingsForm(forms.ModelForm):

    class Meta:

        model = RolePageSettings

        fields = [
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
        ]

        widgets = {
            'role_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Role name'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'role-name'}),
            'farmer_description': forms.Textarea(attrs={'rows': 3}),
            'doctor_description': forms.Textarea(attrs={'rows': 3}),
            'consultant_description': forms.Textarea(attrs={'rows': 3}),
        }