from django.db import models
from accounts.models import Farmer


class ServiceRequest(models.Model):
    farmer = models.ForeignKey(
    Farmer,
    on_delete=models.CASCADE,
    null=True,
    blank=True
    )

    SERVICE_CHOICES = [
        ('Crop Advisory', 'Crop Advisory'),
        ('Soil Testing', 'Soil Testing'),
        ('Disease Identification', 'Disease Identification'),
        ('Plant Doctor', 'Plant Doctor'),
        ('Farmer Consultation', 'Farmer Consultation'),
    ]

    service_type = models.CharField(
        max_length=100,
        choices=SERVICE_CHOICES
    )

    name = models.CharField(max_length=100)

    email = models.EmailField()

    phone = models.CharField(max_length=15)

    address = models.TextField()

    crop_name = models.CharField(
        max_length=100
    )

    problem = models.TextField()

    image = models.ImageField(
        upload_to='service_requests/'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name