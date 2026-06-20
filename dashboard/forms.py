from django import forms
from django.contrib.auth import get_user_model

from accounts.models import (
    AccessCode,
    AdminProfile,
    FooterSettings,
    RegistrationField,
    Role,
    RolePageSettings,
    SiteSettings,
    WhyChooseUs,
)
from consultation.models import ConsultationTopic
from farmer_support.models import CropProblemGuide
from machinery.models import Machinery
from products.models import Crop, SeedVariety
from services.models import ServiceInfo


User = get_user_model()


class ProductForm(forms.ModelForm):

    class Meta:
        model = SeedVariety
        fields = [
            'crop',
            'name',
            'slug',
            'category',
            'image',
            'hero_image',
            'soil_type',
            'season',
            'water_requirement',
            'description',
            'specifications',
            'price',
            'stock',
            'related_products',
            'display_order',
            'is_active',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'specifications': forms.Textarea(attrs={'rows': 4}),
            'related_products': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['crop'].queryset = Crop.objects.order_by('name')
        self.fields['crop'].label_from_instance = lambda crop: f"{crop.name} {'(Inactive)' if not crop.is_active else ''}".strip()


class CropForm(forms.ModelForm):

    status = forms.ChoiceField(
        choices=((True, 'Active'), (False, 'Inactive')),
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial=True,
    )

    class Meta:
        model = Crop
        fields = ['name', 'image', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Crop name'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional crop description'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['status'].initial = self.instance.is_active

    def save(self, commit=True):
        crop = super().save(commit=False)
        crop.is_active = self.cleaned_data.get('status') in (True, 'True', 'true', '1', 1)
        if commit:
            crop.save()
        return crop


class ServiceInfoForm(forms.ModelForm):

    class Meta:
        model = ServiceInfo
        fields = [
            'title',
            'category',
            'slug',
            'short_description',
            'full_description',
            'image',
            'hero_banner_image',
            'features',
            'benefits',
            'process_steps',
            'requirements',
            'why_choose',
            'related_services',
            'display_order',
            'is_active',
        ]
        widgets = {
            'short_description': forms.Textarea(attrs={'rows': 3}),
            'full_description': forms.Textarea(attrs={'rows': 5}),
            'features': forms.Textarea(attrs={'rows': 4}),
            'benefits': forms.Textarea(attrs={'rows': 4}),
            'process_steps': forms.Textarea(attrs={'rows': 4}),
            'requirements': forms.Textarea(attrs={'rows': 4}),
            'why_choose': forms.Textarea(attrs={'rows': 4}),
            'related_services': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }


class ConsultationTopicForm(forms.ModelForm):

    class Meta:
        model = ConsultationTopic
        fields = [
            'title',
            'slug',
            'icon',
            'category',
            'image',
            'hero_image',
            'short_summary',
            'detailed_description',
            'benefits',
            'use_cases',
            'guidance_steps',
            'display_order',
            'is_active',
        ]
        widgets = {
            'short_summary': forms.Textarea(attrs={'rows': 3}),
            'detailed_description': forms.Textarea(attrs={'rows': 5}),
            'benefits': forms.Textarea(attrs={'rows': 4}),
            'use_cases': forms.Textarea(attrs={'rows': 4}),
            'guidance_steps': forms.Textarea(attrs={'rows': 4}),
        }


class CropProblemGuideForm(forms.ModelForm):

    class Meta:
        model = CropProblemGuide
        fields = [
            'title',
            'slug',
            'icon',
            'image',
            'hero_image',
            'short_summary',
            'description',
            'symptoms',
            'causes',
            'prevention_methods',
            'recommended_actions',
            'expert_advice',
            'display_order',
            'is_active',
        ]
        widgets = {
            'short_summary': forms.Textarea(attrs={'rows': 3}),
            'description': forms.Textarea(attrs={'rows': 5}),
            'symptoms': forms.Textarea(attrs={'rows': 4}),
            'causes': forms.Textarea(attrs={'rows': 4}),
            'prevention_methods': forms.Textarea(attrs={'rows': 4}),
            'recommended_actions': forms.Textarea(attrs={'rows': 4}),
            'expert_advice': forms.Textarea(attrs={'rows': 4}),
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
            'site_name',
            'logo',
            'hero_background',
            'mobile_hero_background',
            'hero_video',
        ]


class WhyChooseUsForm(forms.ModelForm):

    class Meta:

        model = WhyChooseUs

        fields = [
            'icon',
            'title'
        ]


class FooterSettingsForm(forms.ModelForm):

    class Meta:

        model = FooterSettings

        fields = '__all__'


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


class AdminProfileForm(forms.ModelForm):

    first_name = forms.CharField(label='Full Name', widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    class Meta:
        model = AdminProfile
        fields = ['profile_photo', 'phone_number', 'role']
        widgets = {
            'profile_photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)
        user = self.instance.user if self.instance and self.instance.pk else None
        if user:
            self.fields['first_name'].initial = self.instance.full_name or user.get_full_name()
            self.fields['email'].initial = user.email
            self.fields['username'].initial = user.username
            self.fields['is_active'].initial = user.is_active

    def clean_role(self):
        role = self.cleaned_data['role']
        request_profile = getattr(self.request_user, 'agritech_profile', None)
        is_super_admin = self.request_user and (self.request_user.is_superuser or (request_profile and request_profile.is_super_admin))

        if role == AdminProfile.ROLE_SUPER_ADMIN and not is_super_admin:
            raise forms.ValidationError('Only Super Admins can assign Super Admin role.')

        if self.instance and self.instance.pk and self.instance.is_super_admin and role != AdminProfile.ROLE_SUPER_ADMIN:
            remaining = AdminProfile.objects.filter(role=AdminProfile.ROLE_SUPER_ADMIN).exclude(pk=self.instance.pk).exists()
            if not remaining:
                raise forms.ValidationError('At least one Super Admin must remain.')

        return role

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['username']
        user.is_active = self.cleaned_data['is_active']
        user.is_staff = True
        user.is_superuser = profile.role == AdminProfile.ROLE_SUPER_ADMIN
        if commit:
            user.save()
            profile.full_name = self.cleaned_data['first_name']
            profile.save()
        return profile


class AdminCreateForm(forms.Form):

    full_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    profile_photo = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    role = forms.ChoiceField(choices=AdminProfile.ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)

    def clean_role(self):
        role = self.cleaned_data['role']
        request_profile = getattr(self.request_user, 'agritech_profile', None)
        is_super_admin = self.request_user and (self.request_user.is_superuser or (request_profile and request_profile.is_super_admin))

        if role == AdminProfile.ROLE_SUPER_ADMIN and not is_super_admin:
            raise forms.ValidationError('Only Super Admins can create Super Admins.')

        return role

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already exists.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already exists.')
        return email

    def save(self):
        role = self.cleaned_data['role']
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['full_name'],
            is_staff=True,
            is_superuser=role == AdminProfile.ROLE_SUPER_ADMIN,
            is_active=True,
        )
        return AdminProfile.objects.create(
            user=user,
            full_name=self.cleaned_data['full_name'],
            phone_number=self.cleaned_data['phone_number'],
            profile_photo=self.cleaned_data.get('profile_photo'),
            role=role,
            email_verified=True,
            phone_verified=True,
        )


class AccessCodeManagementForm(forms.Form):

    ACTION_UPDATE = 'update'
    ACTION_ROTATE = 'rotate'
    ACTION_REGENERATE = 'regenerate'

    ACTION_CHOICES = (
        (ACTION_UPDATE, 'Update'),
        (ACTION_ROTATE, 'Rotate'),
        (ACTION_REGENERATE, 'Regenerate'),
    )

    code_type = forms.ChoiceField(
        choices=AccessCode.CODE_TYPE_CHOICES,
        widget=forms.HiddenInput(),
    )
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.HiddenInput(),
    )
    code_value = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new access code'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        code_value = cleaned_data.get('code_value')

        if action == self.ACTION_UPDATE and not code_value:
            raise forms.ValidationError('Enter a code value to update this access code.')

        return cleaned_data


class RegistrationFieldForm(forms.ModelForm):

    class Meta:
        model = RegistrationField
        fields = ['role', 'label', 'key', 'field_type', 'help_text', 'choices', 'is_required', 'is_active', 'sort_order']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'label': forms.TextInput(attrs={'class': 'form-control'}),
            'key': forms.TextInput(attrs={'class': 'form-control'}),
            'field_type': forms.Select(attrs={'class': 'form-select'}),
            'help_text': forms.TextInput(attrs={'class': 'form-control'}),
            'choices': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class RoleManagementForm(forms.ModelForm):

    class Meta:
        model = Role
        fields = ['name', 'slug', 'description', 'icon', 'register_url', 'dashboard_url', 'permissions', 'is_active', 'is_system']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'icon': forms.TextInput(attrs={'class': 'form-control'}),
            'register_url': forms.TextInput(attrs={'class': 'form-control'}),
            'dashboard_url': forms.TextInput(attrs={'class': 'form-control'}),
            'permissions': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_system': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
