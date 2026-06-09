from django.db import models
from accounts.models import Farmer


class CropProblem(models.Model):
    farmer = models.ForeignKey(
    Farmer,
    on_delete=models.CASCADE,
    null=True,
    blank=True
    )

    name = models.CharField(max_length=100)

    email = models.EmailField()

    phone = models.CharField(max_length=15)

    crop_name = models.CharField(max_length=100)

    problem = models.TextField()

    image = models.ImageField(
        upload_to='crop_problems/'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


class AdminReply(models.Model):

    crop_problem = models.OneToOneField(
        CropProblem,
        on_delete=models.CASCADE
    )

    reply = models.TextField()

    def __str__(self):
        return self.crop_problem.name