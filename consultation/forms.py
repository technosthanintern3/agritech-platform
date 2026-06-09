from django import forms
from .models import ConsultationRequest


class ConsultationForm(forms.ModelForm):

    class Meta:
        model = ConsultationRequest

        fields = '__all__'

        widgets = {
            'preferred_date': forms.DateInput(
                attrs={'type': 'date'}
            )
        }