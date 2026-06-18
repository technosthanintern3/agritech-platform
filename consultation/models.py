from django.db import models
from accounts.models import Farmer
from accounts.models import Doctor, Consultant

class ConsultationRequest(models.Model):

    STATUS_CHOICES = [

        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),

    ]

    farmer = models.ForeignKey(
        Farmer,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    assigned_doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consultation_requests'
    )

    assigned_consultant = models.ForeignKey(
        Consultant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consultation_requests'
    )

    name = models.CharField(max_length=100)

    email = models.EmailField()

    phone = models.CharField(max_length=15)

    address = models.TextField()

    preferred_date = models.DateField()

    message = models.TextField()

    doctor_reply = models.TextField(blank=True, null=True)

    consultant_reply = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name