from django.db import models


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
        on_delete=models.CASCADE
    )

    name = models.CharField(
        max_length=100
    )

    from django.core.validators import(
        MinValueValidator,
        MaxValueValidator
    )
    
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )

    comment = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.name