from django import forms
from .models import TractorBooking


class TractorBookingForm(forms.ModelForm):

    class Meta:

        model = TractorBooking

        exclude = ['farmer']

        widgets = {

            'machinery_type': forms.Select(
                attrs={
                    'class': 'form-control',
                    'id': 'id_machinery_type'
                }
            ),

            'name': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'phone': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'address': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3
                }
            ),

            'booking_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),

            'purpose': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4
                }
            )

        }