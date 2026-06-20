import re

from django import forms
from django.utils.safestring import mark_safe

from .models import AccessCode, Farmer, Doctor, Consultant, RegistrationField, Role


def validate_password_strength(password):

    errors = []

    if len(password or '') < 8:
        errors.append('Minimum 8 characters')

    if not re.search(r'[A-Z]', password or ''):
        errors.append('1 Uppercase letter')

    if not re.search(r'[a-z]', password or ''):
        errors.append('1 Lowercase letter')

    if not re.search(r'[0-9]', password or ''):
        errors.append('1 Number')

    if not re.search(r'[@$!%*?&#]', password or ''):
        errors.append('1 Special character')

    if errors:

        raise forms.ValidationError(
            mark_safe(
                '<b>Password must contain:</b>'
                '<ul>'
                + ''.join(f'<li>{error}</li>' for error in errors)
                + '</ul>'
            )
        )


class CommonLoginForm(forms.Form):

    ROLE_CHOICES = (
        ('farmer', 'Farmer'),
        ('doctor', 'Doctor'),
        ('consultant', 'Consultant'),
        ('admin', 'Admin'),
    )

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.Select(
            attrs={
                'class': 'form-select',
            }
        )
    )

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email'
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter your password',
                'autocomplete': 'current-password',
            }
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        dynamic_choices = list(
            Role.objects.filter(is_active=True).values_list('slug', 'name').order_by('name')
        )
        if dynamic_choices:
            self.fields['role'].choices = dynamic_choices


class PasswordChangeForm(forms.Form):

    current_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Current password',
                'autocomplete': 'current-password',
            }
        )
    )

    new_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'New password',
                'autocomplete': 'new-password',
            }
        )
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Confirm new password',
                'autocomplete': 'new-password',
            }
        )
    )

    def clean_new_password(self):
        password = self.cleaned_data.get('new_password')
        validate_password_strength(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('new_password') != cleaned_data.get('confirm_password'):
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data


class ForgotPasswordRequestForm(forms.Form):

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter your registered email',
                'autocomplete': 'email',
            }
        )
    )


class ForgotPasswordOTPForm(forms.Form):

    otp_code = forms.CharField(
        min_length=6,
        max_length=6,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter OTP code',
                'inputmode': 'numeric',
                'autocomplete': 'one-time-code',
            }
        )
    )


class PasswordResetForm(forms.Form):

    new_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'New password',
                'autocomplete': 'new-password',
            }
        )
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Confirm new password',
                'autocomplete': 'new-password',
            }
        )
    )

    def clean_new_password(self):
        password = self.cleaned_data.get('new_password')
        validate_password_strength(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('new_password') != cleaned_data.get('confirm_password'):
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data


class AvailabilityStatusForm(forms.Form):
    """Validate explicit availability updates from staff dashboards."""

    is_online = forms.TypedChoiceField(
        choices=((True, 'Online'), (False, 'Offline')),
        coerce=lambda value: value == 'True',
        widget=forms.HiddenInput,
    )


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

        validate_password_strength(password)

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


class DoctorRegistrationForm(forms.ModelForm):

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Confirm Password'
            }
        )
    )

    class Meta:

        model = Doctor

        fields = [
            'full_name',
            'email',
            'phone',
            'aadhaar_number',
            'pan_number',
            'qualification',
            'experience',
            'specialization',
            'certification_upload',
            'identity_photo_upload',
            'profile_photo',
            'password'
        ]

        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'aadhaar_number': forms.TextInput(attrs={'class': 'form-control'}),
            'pan_number': forms.TextInput(attrs={'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'experience': forms.TextInput(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_dynamic_registration_fields(self, RegistrationField.ROLE_DOCTOR)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        validate_password_strength(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('confirm_password'):
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data


class ConsultantRegistrationForm(forms.ModelForm):

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Confirm Password'
            }
        )
    )

    class Meta:

        model = Consultant

        fields = [
            'full_name',
            'email',
            'phone',
            'aadhaar_number',
            'pan_number',
            'qualification',
            'experience',
            'specialization',
            'certification_upload',
            'identity_photo_upload',
            'profile_photo',
            'password'
        ]

        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'aadhaar_number': forms.TextInput(attrs={'class': 'form-control'}),
            'pan_number': forms.TextInput(attrs={'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'experience': forms.TextInput(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_dynamic_registration_fields(self, RegistrationField.ROLE_CONSULTANT)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        validate_password_strength(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('confirm_password'):
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data


class AdminRegistrationForm(forms.Form):

    full_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Full Name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email'})
    )
    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Phone Number'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Password'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )
    admin_code = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Admin Code'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_dynamic_registration_fields(self, RegistrationField.ROLE_ADMIN)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        validate_password_strength(password)
        return password

    def clean_admin_code(self):
        admin_code = self.cleaned_data.get('admin_code')
        access_code_type = AccessCode.resolve_role(admin_code)

        if not access_code_type:
            raise forms.ValidationError('Invalid Admin Code')

        self.access_code_type = access_code_type
        return admin_code

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('confirm_password'):
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data


def add_dynamic_registration_fields(form, role):

    dynamic_fields = RegistrationField.objects.filter(role=role, is_active=True)

    for field in dynamic_fields:
        field_name = f'dynamic_{field.key}'
        attrs = {'class': 'form-control'}
        kwargs = {
            'label': field.label,
            'required': field.is_required,
            'help_text': field.help_text,
        }

        if field.field_type == RegistrationField.TYPE_EMAIL:
            form.fields[field_name] = forms.EmailField(widget=forms.EmailInput(attrs=attrs), **kwargs)
        elif field.field_type == RegistrationField.TYPE_NUMBER:
            form.fields[field_name] = forms.DecimalField(widget=forms.NumberInput(attrs=attrs), **kwargs)
        elif field.field_type == RegistrationField.TYPE_DATE:
            form.fields[field_name] = forms.DateField(widget=forms.DateInput(attrs={**attrs, 'type': 'date'}), **kwargs)
        elif field.field_type == RegistrationField.TYPE_TEXTAREA:
            form.fields[field_name] = forms.CharField(widget=forms.Textarea(attrs={**attrs, 'rows': 3}), **kwargs)
        elif field.field_type == RegistrationField.TYPE_DROPDOWN:
            choices = [('', 'Select')] + [(choice, choice) for choice in field.choice_list()]
            form.fields[field_name] = forms.ChoiceField(choices=choices, widget=forms.Select(attrs={'class': 'form-select'}), **kwargs)
        elif field.field_type == RegistrationField.TYPE_RADIO:
            choices = [(choice, choice) for choice in field.choice_list()]
            form.fields[field_name] = forms.ChoiceField(choices=choices, widget=forms.RadioSelect(attrs={'class': 'form-check-input'}), **kwargs)
        elif field.field_type == RegistrationField.TYPE_CHECKBOX:
            choices = [(choice, choice) for choice in field.choice_list()]
            if choices:
                form.fields[field_name] = forms.MultipleChoiceField(
                    choices=choices,
                    widget=forms.CheckboxSelectMultiple,
                    **kwargs
                )
            else:
                form.fields[field_name] = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), **kwargs)
        elif field.field_type == RegistrationField.TYPE_FILE:
            form.fields[field_name] = forms.FileField(widget=forms.ClearableFileInput(attrs=attrs), **kwargs)
        else:
            form.fields[field_name] = forms.CharField(widget=forms.TextInput(attrs=attrs), **kwargs)


def extract_dynamic_registration_data(cleaned_data):

    dynamic_data = {}

    for key, value in cleaned_data.items():
        if not key.startswith('dynamic_'):
            continue

        clean_key = key.replace('dynamic_', '', 1)
        dynamic_data[clean_key] = value

    return dynamic_data


class OTPVerificationForm(forms.Form):

    email_otp = forms.CharField(
        min_length=6,
        max_length=6,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email OTP'})
    )
    phone_otp = forms.CharField(
        min_length=6,
        max_length=6,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Mobile OTP'})
    )


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

            'profile_picture': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control',
                    'accept': 'image/*'
                }
            ),

        }


class DoctorProfileForm(forms.ModelForm):

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Leave blank to keep current password'
            }
        )
    )

    identity_photo_upload = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    class Meta:

        model = Doctor

        fields = [
            'full_name',
            'email',
            'profile_photo',
            'password',
            'qualification',
            'experience',
            'specialization',
            'certification_upload',
            'aadhaar_number',
            'pan_number',
            'identity_photo_upload',
        ]

        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            'profile_photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'experience': forms.TextInput(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'certification_upload': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'aadhaar_number': forms.TextInput(attrs={'class': 'form-control'}),
            'pan_number': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ConsultantProfileForm(forms.ModelForm):

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Leave blank to keep current password'
            }
        )
    )

    identity_photo_upload = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    class Meta:

        model = Consultant

        fields = [
            'full_name',
            'email',
            'profile_photo',
            'password',
            'qualification',
            'experience',
            'specialization',
            'certification_upload',
            'aadhaar_number',
            'pan_number',
            'identity_photo_upload',
        ]

        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            'profile_photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'experience': forms.TextInput(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'certification_upload': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'aadhaar_number': forms.TextInput(attrs={'class': 'form-control'}),
            'pan_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
