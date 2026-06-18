from django import forms
from .models import ConsultationRequest


class ConsultationForm(forms.ModelForm):

    class Meta:
        model = ConsultationRequest

        fields = [
            'name',
            'email',
            'phone',
            'address',
            'preferred_date',
            'message',
        ]

        widgets = {
            'preferred_date': forms.DateInput(
                attrs={'type': 'date'}
            )
        }


class ConsultationStatusReplyForm(forms.ModelForm):

    class Meta:
        model = ConsultationRequest

        fields = ['status']

        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'})
        }