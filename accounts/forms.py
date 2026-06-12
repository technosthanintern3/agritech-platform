import re

from django import forms
from django.utils.safestring import mark_safe

from .models import Farmer


class FarmerRegistrationForm(forms.ModelForm):

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Confirm Password'
            }
        )
    )

    class Meta:

        model = Farmer

        fields = [
            'name',
            'email',
            'phone',
            'address',
            'password'
        ]

        widgets = {

            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter Full Name'
                }
            ),

            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter Email'
                }
            ),

            'phone': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter Phone Number'
                }
            ),

            'address': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Enter Address'
                }
            ),

            'password': forms.PasswordInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter Password'
                }
            )

        }

    def clean_password(self):

        password = self.cleaned_data.get('password')

        errors = []

        if len(password) < 8:
            errors.append("Minimum 8 characters")

        if not re.search(r'[A-Z]', password):
            errors.append("1 Uppercase letter")

        if not re.search(r'[a-z]', password):
            errors.append("1 Lowercase letter")

        if not re.search(r'[0-9]', password):
            errors.append("1 Number")

        if not re.search(r'[@$!%*?&#]', password):
            errors.append("1 Special character")

        if errors:

            raise forms.ValidationError(
                mark_safe(
                    "<b>Password must contain:</b>"
                    "<ul>"
                    + "".join(
                        f"<li>{error}</li>"
                        for error in errors
                    )
                    + "</ul>"
                )
            )

        return password

    def clean(self):

        cleaned_data = super().clean()

        password = cleaned_data.get(
            'password'
        )

        confirm_password = cleaned_data.get(
            'confirm_password'
        )

        if password != confirm_password:

            raise forms.ValidationError(
                "Passwords do not match."
            )

        return cleaned_data


class EditProfileForm(forms.ModelForm):

    class Meta:

        model = Farmer

        fields = [
            'profile_picture',
            'name',
            'email',
            'phone',
            'address'
        ]

        widgets = {

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

        }