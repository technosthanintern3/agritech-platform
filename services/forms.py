from django import forms
from .models import ServiceRequest


class ServiceRequestForm(forms.ModelForm):

    class Meta:
        model = ServiceRequest

        fields = [
            'service_type',
            'name',
            'email',
            'phone',
            'address',
            'crop_name',
            'problem',
            'image'
        ]