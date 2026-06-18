from django.db import models


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
    last_login_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.full_name

    @property
    def is_online(self):
        if not self.last_login_time:
            return False

        from django.utils import timezone

        return (
            timezone.now() - self.last_login_time
        ).total_seconds() <= 900


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
    last_login_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.full_name

    @property
    def is_online(self):
        if not self.last_login_time:
            return False

        from django.utils import timezone

        return (
            timezone.now() - self.last_login_time
        ).total_seconds() <= 900


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