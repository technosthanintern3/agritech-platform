from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from accounts.models import Farmer


class Crop(models.Model):

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class SeedVariety(models.Model):

    crop = models.ForeignKey(
        Crop,
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=100)

    image = models.ImageField(
        upload_to='seeds/'
    )

    soil_type = models.CharField(
        max_length=100
    )

    season = models.CharField(
        max_length=100
    )

    water_requirement = models.CharField(
        max_length=100
    )

    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return self.name


class Review(models.Model):

    product = models.ForeignKey(
        SeedVariety,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    farmer = models.ForeignKey(
        Farmer,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='product_reviews'
    )
    name = models.CharField(max_length=100)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)
    is_hidden = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.product.name}'
