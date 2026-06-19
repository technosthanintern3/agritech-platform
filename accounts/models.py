import uuid

from django.db import models
from django.utils.text import slugify


class Farmer(models.Model):

    name = models.CharField(max_length=100)

    email = models.EmailField(
        unique=True
    )

    phone = models.CharField(
        max_length=15
    )

    address = models.TextField()

    password = models.CharField(
        max_length=255
    )

    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)

    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


class Doctor(models.Model):

    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    aadhaar_number = models.CharField(max_length=20)
    pan_number = models.CharField(max_length=20)
    identity_photo_upload = models.ImageField(upload_to='doctor_identity_docs/')
    profile_photo = models.ImageField(
        upload_to='doctor_profiles/',
        blank=True,
        null=True
    )
    password = models.CharField(max_length=255)
    registration_date = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    is_active_status = models.BooleanField(default=False)
    identity_edit_allowed = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    last_login_time = models.DateTimeField(blank=True, null=True)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.full_name

class Consultant(models.Model):

    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    aadhaar_number = models.CharField(max_length=20)
    pan_number = models.CharField(max_length=20)
    identity_photo_upload = models.ImageField(upload_to='consultant_identity_docs/')
    profile_photo = models.ImageField(
        upload_to='consultant_profiles/',
        blank=True,
        null=True
    )
    password = models.CharField(max_length=255)
    registration_date = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    is_active_status = models.BooleanField(default=False)
    identity_edit_allowed = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    last_login_time = models.DateTimeField(blank=True, null=True)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.full_name

class Role(models.Model):

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=120)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='\U0001f464')
    register_url = models.CharField(max_length=255)
    dashboard_url = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class IdentityChangeRequest(models.Model):

    ROLE_DOCTOR = 'doctor'
    ROLE_CONSULTANT = 'consultant'

    ROLE_CHOICES = (
        (ROLE_DOCTOR, 'Doctor'),
        (ROLE_CONSULTANT, 'Consultant'),
    )

    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    account_id = models.PositiveIntegerField()
    account_name = models.CharField(max_length=100)
    email = models.EmailField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    admin_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.account_name} - {self.get_role_display()}'


class AdminProfile(models.Model):

    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='agritech_profile')
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class RegistrationOTP(models.Model):

    ROLE_FARMER = 'farmer'
    ROLE_DOCTOR = 'doctor'
    ROLE_CONSULTANT = 'consultant'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = (
        (ROLE_FARMER, 'Farmer'),
        (ROLE_DOCTOR, 'Doctor'),
        (ROLE_CONSULTANT, 'Consultant'),
        (ROLE_ADMIN, 'Admin'),
    )

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    payload = models.JSONField()
    profile_photo = models.ImageField(upload_to='registration_otps/profile_photos/', blank=True, null=True)
    identity_photo_upload = models.ImageField(upload_to='registration_otps/identity_docs/', blank=True, null=True)
    email_otp_hash = models.CharField(max_length=255)
    phone_otp_hash = models.CharField(max_length=255)
    resend_count = models.PositiveSmallIntegerField(default=0)
    verify_attempts = models.PositiveSmallIntegerField(default=0)
    expires_at = models.DateTimeField()
    is_consumed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.email} - {self.get_role_display()}'


class SiteSettings(models.Model):

    site_name = models.CharField(max_length=100)

    logo = models.ImageField(
        upload_to="site_logo/",
        blank=True,
        null=True
    )

    hero_background = models.ImageField(
        upload_to="hero_background/",
        blank=True,
        null=True
    )

    mobile_hero_background = models.ImageField(
        upload_to="hero_background/mobile/",
        blank=True,
        null=True
    )

    hero_video = models.FileField(
        upload_to="hero_videos/",
        blank=True,
        null=True
    )

    def save(self,*args,**kwargs):
        self.pk = 1
        super().save(*args,**kwargs)

    def __str__(self):
        return "Site Settings"

class WhyChooseUs(models.Model):

    icon = models.CharField(
        max_length=50
    )

    title = models.CharField(
        max_length=100
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title

class FooterSettings(models.Model):

    company_description = models.TextField()

    address = models.TextField()

    phone = models.CharField(
        max_length=20
    )

    email = models.EmailField()

    facebook = models.URLField(
        blank=True,
        null=True
    )

    instagram = models.URLField(
        blank=True,
        null=True
    )

    youtube = models.URLField(
        blank=True,
        null=True
    )

    linkedin = models.URLField(
        blank=True,
        null=True
    )

    copyright_text = models.CharField(
        max_length=200,
        default="© AgroSthan"
    )

    def save(self,*args,**kwargs):
        self.pk = 1
        super().save(*args,**kwargs)

    def __str__(self):
        return "Footer Settings"


class RolePageSettings(models.Model):

    role_name = models.CharField(max_length=100, unique=True, default='Farmer/User')
    slug = models.SlugField(max_length=120, unique=True, default='farmer-user')

    farmer_title = models.CharField(max_length=100, default='Farmer/User')
    farmer_description = models.TextField(
        default='Register as a Farmer and access products, machinery and consultations.'
    )
    farmer_icon = models.CharField(max_length=50, default='👨‍🌾')

    doctor_title = models.CharField(max_length=100, default='Doctor')
    doctor_description = models.TextField(
        default='Register as an Agriculture Doctor and manage farmer requests.'
    )
    doctor_icon = models.CharField(max_length=50, default='🩺')

    consultant_title = models.CharField(max_length=100, default='Consultant')
    consultant_description = models.TextField(
        default='Register as an Agriculture Consultant and provide expert guidance.'
    )
    consultant_icon = models.CharField(max_length=50, default='💼')

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.role_name
