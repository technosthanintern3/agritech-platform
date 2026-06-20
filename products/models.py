from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify

from accounts.models import Farmer


class Crop(models.Model):

    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='crops/', blank=True, null=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class SeedVariety(models.Model):

    crop = models.ForeignKey(
        Crop,
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=100)

    slug = models.SlugField(max_length=140, unique=True, blank=True, null=True)

    category = models.CharField(max_length=120, blank=True)

    image = models.ImageField(
        upload_to='seeds/'
    )

    hero_image = models.ImageField(
        upload_to='seeds/hero/',
        blank=True,
        null=True
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

    specifications = models.TextField(
        blank=True,
        help_text='Enter one specification per line'
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    stock = models.PositiveIntegerField(default=0)

    related_products = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False
    )

    is_active = models.BooleanField(default=True)

    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or 'product'
            slug = base_slug
            counter = 2
            while SeedVariety.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug

        super().save(*args, **kwargs)

    def get_specifications_list(self):
        return [item for item in self.specifications.splitlines() if item.strip()]

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
