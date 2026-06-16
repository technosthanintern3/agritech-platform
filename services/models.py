from django.db import models
from accounts.models import Farmer


class ServiceRequest(models.Model):

    farmer = models.ForeignKey(
        Farmer,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    service_type = models.ForeignKey(
        'ServiceInfo',
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=100)

    email = models.EmailField()

    phone = models.CharField(max_length=15)

    address = models.TextField()

    crop_name = models.CharField(max_length=100)

    problem = models.TextField()

    image = models.ImageField(
        upload_to='service_requests/'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name
    

class ServiceInfo(models.Model):

    title = models.CharField(
        max_length=200
    )

    slug = models.SlugField(
        unique=True
    )

    short_description = models.TextField()

    full_description = models.TextField()

    image = models.ImageField(
        upload_to='service_images/',
        blank=True,
        null=True
    )

    benefits = models.TextField(
        help_text="Enter one benefit per line",
        blank=True
    )

    why_choose = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def get_benefits_list(self):
        return self.benefits.splitlines()

    def __str__(self):
        return self.title