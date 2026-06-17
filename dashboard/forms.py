from django import forms
from products.models import SeedVariety
from machinery.models import Machinery

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