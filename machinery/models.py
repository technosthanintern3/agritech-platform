from django.db import models
from accounts.models import Farmer


class Machinery(models.Model):

    name = models.CharField(
        max_length=100
    )

    image = models.ImageField(
        upload_to='machinery/'
    )

    description = models.TextField()

    price_per_day = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return self.name


class TractorBooking(models.Model):

    MACHINERY_CHOICES = [
        ('Tractor', 'Tractor'),
        ('Harvester', 'Harvester'),
        ('Rotavator', 'Rotavator'),
        ('Seed Drill', 'Seed Drill'),
        ('Drone', 'Drone')
    ]

    farmer = models.ForeignKey(
        Farmer,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    machinery_type = models.CharField(
        max_length=50,
        choices=MACHINERY_CHOICES,
        default='Tractor'
    )

    name = models.CharField(
        max_length=100
    )

    email = models.EmailField()

    phone = models.CharField(
        max_length=15
    )

    address = models.TextField()

    booking_date = models.DateField()

    purpose = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.name} - {self.machinery_type}"