from django.db import models


class SiteSettings(models.Model):

    site_name = models.CharField(
        max_length=200,
        default="AgroSthan"
    )

    logo = models.ImageField(
        upload_to="site/",
        blank=True,
        null=True
    )

    favicon = models.ImageField(
        upload_to="site/",
        blank=True,
        null=True
    )

    hero_image = models.ImageField(
        upload_to="site/",
        blank=True,
        null=True
    )

    hero_video = models.FileField(
        upload_to="site/videos/",
        blank=True,
        null=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    email = models.EmailField(
        blank=True
    )

    footer_text = models.TextField(
        blank=True
    )

    def __str__(self):
        return self.site_name