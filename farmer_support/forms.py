from django import forms
from .models import CropProblem


class CropProblemForm(forms.ModelForm):

    class Meta:
        model = CropProblem

        fields = [
            'name',
            'email',
            'phone',
            'crop_name',
            'problem',
            'image'
        ]