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
    

class SiteSettings(models.Model):

    site_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    logo = models.ImageField(
        upload_to='site_logo/',
        blank=True,
        null=True
    )

    hero_background = models.ImageField(
        upload_to='hero_background/',
        blank=True,
        null=True
    )
    mobile_hero_background = models.ImageField(
        upload_to='hero_background/mobile/',
        blank=True,
        null=True
    )

        

    def __str__(self):

        return self.site_name