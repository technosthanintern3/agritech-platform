from django import forms
from .models import ServiceRequest, ServiceInfo


class ServiceRequestForm(forms.ModelForm):

    service_type = forms.ModelChoiceField(
        queryset=ServiceInfo.objects.all(),
        empty_label="Select Service",
        widget=forms.Select(
            attrs={
                'class': 'form-select'
            }
        )
    )

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

        widgets = {

            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter your name'
                }
            ),

            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter your email'
                }
            ),

            'phone': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter your phone number'
                }
            ),

            'address': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Enter your address'
                }
            ),

            'crop_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter crop name'
                }
            ),

            'problem': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Describe your problem'
                }
            ),

            'image': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control'
                }
            ),
        }