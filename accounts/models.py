import secrets
import uuid

from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.utils import timezone
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

    STATUS_PENDING = 'pending'
    STATUS_UNDER_REVIEW = 'under_review'
    STATUS_VERIFIED = 'verified'
    STATUS_REJECTED = 'rejected'
    VERIFICATION_STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_UNDER_REVIEW, 'Under Review'),
        (STATUS_VERIFIED, 'Verified'),
        (STATUS_REJECTED, 'Rejected'),
    )

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
    qualification = models.CharField(max_length=150, blank=True)
    experience = models.CharField(max_length=100, blank=True)
    specialization = models.CharField(max_length=150, blank=True)
    certification_upload = models.FileField(upload_to='doctor_certifications/', blank=True, null=True)
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    verification_note = models.TextField(blank=True)
    dynamic_fields = models.JSONField(default=dict, blank=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    last_login_time = models.DateTimeField(blank=True, null=True)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.full_name

class Consultant(models.Model):

    STATUS_PENDING = 'pending'
    STATUS_UNDER_REVIEW = 'under_review'
    STATUS_VERIFIED = 'verified'
    STATUS_REJECTED = 'rejected'
    VERIFICATION_STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_UNDER_REVIEW, 'Under Review'),
        (STATUS_VERIFIED, 'Verified'),
        (STATUS_REJECTED, 'Rejected'),
    )

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
    qualification = models.CharField(max_length=150, blank=True)
    experience = models.CharField(max_length=100, blank=True)
    specialization = models.CharField(max_length=150, blank=True)
    certification_upload = models.FileField(upload_to='consultant_certifications/', blank=True, null=True)
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    verification_note = models.TextField(blank=True)
    dynamic_fields = models.JSONField(default=dict, blank=True)
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
    permissions = models.JSONField(default=dict, blank=True)
    is_system = models.BooleanField(default=False)
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

    ROLE_ADMIN = 'admin'
    ROLE_SUPER_ADMIN = 'super_admin'
    ROLE_CHOICES = (
        (ROLE_ADMIN, 'Admin'),
        (ROLE_SUPER_ADMIN, 'Super Admin'),
    )

    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='agritech_profile')
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20)
    profile_photo = models.ImageField(upload_to='admin_profiles/', blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_ADMIN)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def is_super_admin(self):
        return self.role == self.ROLE_SUPER_ADMIN or self.user.is_superuser

    def __str__(self):
        return self.full_name


class AccessCode(models.Model):

    ROLE_ADMIN = 'admin'
    ROLE_SUPER_ADMIN = 'super_admin'
    CODE_TYPE_CHOICES = (
        (ROLE_ADMIN, 'Admin Access Code'),
        (ROLE_SUPER_ADMIN, 'Super Admin Access Code'),
    )

    code_type = models.CharField(max_length=20, choices=CODE_TYPE_CHOICES, unique=True)
    code_hash = models.CharField(max_length=255)
    previous_code_hash = models.CharField(max_length=255, blank=True, default='')
    rotation_count = models.PositiveIntegerField(default=0)
    last_rotated_at = models.DateTimeField(blank=True, null=True)
    updated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='updated_access_codes',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code_type']

    @classmethod
    def generate_code(cls):
        return secrets.token_hex(8).upper()

    @classmethod
    def resolve_role(cls, raw_code):
        if not raw_code:
            return None

        for access_code in cls.objects.all():
            if check_password(raw_code, access_code.code_hash):
                return access_code.code_type

        return None

    def rotate_code(self, raw_code=None, updated_by=None):
        if raw_code is None:
            raw_code = self.generate_code()

        if self.code_hash:
            self.previous_code_hash = self.code_hash
            self.rotation_count = self.rotation_count + 1
            self.last_rotated_at = timezone.now()
        else:
            self.rotation_count = 0
            self.last_rotated_at = timezone.now()

        self.code_hash = make_password(raw_code)
        if updated_by is not None:
            self.updated_by = updated_by
        self.save()
        return raw_code

    def update_code(self, raw_code, updated_by=None):
        return self.rotate_code(raw_code=raw_code, updated_by=updated_by)

    def matches(self, raw_code):
        return check_password(raw_code, self.code_hash)

    @property
    def code_label(self):
        return self.get_code_type_display()

    @property
    def masked_code(self):
        return 'Protected'


class RegistrationField(models.Model):

    ROLE_DOCTOR = 'doctor'
    ROLE_CONSULTANT = 'consultant'
    ROLE_ADMIN = 'admin'
    ROLE_CHOICES = (
        (ROLE_DOCTOR, 'Doctor'),
        (ROLE_CONSULTANT, 'Consultant'),
        (ROLE_ADMIN, 'Admin'),
    )

    TYPE_TEXT = 'text'
    TYPE_EMAIL = 'email'
    TYPE_NUMBER = 'number'
    TYPE_DATE = 'date'
    TYPE_DROPDOWN = 'dropdown'
    TYPE_RADIO = 'radio'
    TYPE_CHECKBOX = 'checkbox'
    TYPE_FILE = 'file'
    TYPE_TEXTAREA = 'textarea'
    FIELD_TYPE_CHOICES = (
        (TYPE_TEXT, 'Text'),
        (TYPE_EMAIL, 'Email'),
        (TYPE_NUMBER, 'Number'),
        (TYPE_DATE, 'Date'),
        (TYPE_DROPDOWN, 'Dropdown'),
        (TYPE_RADIO, 'Radio'),
        (TYPE_CHECKBOX, 'Checkbox'),
        (TYPE_FILE, 'File Upload'),
        (TYPE_TEXTAREA, 'Textarea'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    label = models.CharField(max_length=120)
    key = models.SlugField(max_length=140)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPE_CHOICES, default=TYPE_TEXT)
    help_text = models.CharField(max_length=255, blank=True)
    choices = models.TextField(blank=True, help_text='One option per line for dropdown, radio, or checkbox fields.')
    is_required = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['role', 'sort_order', 'label']
        unique_together = ('role', 'key')

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = slugify(self.label).replace('-', '_')
        super().save(*args, **kwargs)

    def choice_list(self):
        return [choice.strip() for choice in self.choices.splitlines() if choice.strip()]

    def __str__(self):
        return f'{self.get_role_display()} - {self.label}'


class VerificationHistory(models.Model):

    ROLE_DOCTOR = 'doctor'
    ROLE_CONSULTANT = 'consultant'
    ROLE_CHOICES = (
        (ROLE_DOCTOR, 'Doctor'),
        (ROLE_CONSULTANT, 'Consultant'),
    )

    ACTION_APPROVED = 'approved'
    ACTION_REJECTED = 'rejected'
    ACTION_REQUESTED_DOCUMENTS = 'requested_documents'
    ACTION_UNDER_REVIEW = 'under_review'
    ACTION_CHOICES = (
        (ACTION_APPROVED, 'Approved'),
        (ACTION_REJECTED, 'Rejected'),
        (ACTION_REQUESTED_DOCUMENTS, 'Requested Additional Documents'),
        (ACTION_UNDER_REVIEW, 'Marked Under Review'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    account_id = models.PositiveIntegerField()
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    note = models.TextField(blank=True)
    performed_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_role_display()} #{self.account_id} - {self.get_action_display()}'


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


class PasswordResetOTP(models.Model):

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
    account_id = models.PositiveIntegerField()
    otp_hash = models.CharField(max_length=255)
    attempt_count = models.PositiveSmallIntegerField(default=0)
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(blank=True, null=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.email} - {self.get_role_display()} reset OTP'


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
