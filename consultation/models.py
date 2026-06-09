from django.db import models
from accounts.models import Farmer


class ConsultationRequest(models.Model):
    farmer = models.ForeignKey(
    Farmer,
    on_delete=models.CASCADE,
    null=True,
    blank=True
    )

    name = models.CharField(max_length=100)

    email = models.EmailField()

    phone = models.CharField(max_length=15)

    address = models.TextField()

    preferred_date = models.DateField()

    message = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name