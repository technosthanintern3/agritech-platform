from django.db import models
from django.utils.text import slugify
from accounts.models import Farmer
from accounts.models import Doctor, Consultant


class ConsultationTopic(models.Model):

    title = models.CharField(max_length=160)

    slug = models.SlugField(unique=True, blank=True)

    icon = models.CharField(max_length=80, default='bi bi-person-video3')

    category = models.CharField(max_length=120, blank=True)

    short_summary = models.TextField()

    detailed_description = models.TextField()

    image = models.ImageField(
        upload_to='consultation_topics/',
        blank=True,
        null=True
    )

    hero_image = models.ImageField(
        upload_to='consultation_topics/hero/',
        blank=True,
        null=True
    )

    benefits = models.TextField(
        help_text='Enter one benefit per line',
        blank=True
    )

    use_cases = models.TextField(
        help_text='Enter one use case per line',
        blank=True
    )

    guidance_steps = models.TextField(
        help_text='Enter one process/guidance step per line',
        blank=True
    )

    display_order = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', 'title']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    def get_benefits_list(self):
        return self.benefits.splitlines()

    def get_use_cases_list(self):
        return self.use_cases.splitlines()

    def get_guidance_steps_list(self):
        return self.guidance_steps.splitlines()

    def __str__(self):
        return self.title

class ConsultationRequest(models.Model):

    STATUS_CHOICES = [

        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),

    ]

    farmer = models.ForeignKey(
        Farmer,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    assigned_doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consultation_requests'
    )

    assigned_consultant = models.ForeignKey(
        Consultant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consultation_requests'
    )

    name = models.CharField(max_length=100)

    email = models.EmailField()

    phone = models.CharField(max_length=15)

    address = models.TextField()

    preferred_date = models.DateField()

    message = models.TextField()

    doctor_reply = models.TextField(blank=True, null=True)

    consultant_reply = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name
