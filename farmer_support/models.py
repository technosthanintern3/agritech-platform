from django.db import models
from django.utils.text import slugify
from accounts.models import Farmer


class CropProblemGuide(models.Model):

    title = models.CharField(max_length=160)

    slug = models.SlugField(unique=True, blank=True)

    icon = models.CharField(max_length=80, default='bi bi-activity')

    short_summary = models.TextField()

    description = models.TextField()

    image = models.ImageField(
        upload_to='crop_problem_guides/',
        blank=True,
        null=True
    )

    hero_image = models.ImageField(
        upload_to='crop_problem_guides/hero/',
        blank=True,
        null=True
    )

    symptoms = models.TextField(
        help_text='Enter one symptom per line',
        blank=True
    )

    causes = models.TextField(
        help_text='Enter one cause per line',
        blank=True
    )

    prevention_methods = models.TextField(
        help_text='Enter one prevention method per line',
        blank=True
    )

    recommended_actions = models.TextField(
        help_text='Enter one recommended action per line',
        blank=True
    )

    expert_advice = models.TextField(blank=True)

    display_order = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', 'title']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    def get_symptoms_list(self):
        return self.symptoms.splitlines()

    def get_prevention_methods_list(self):
        return self.prevention_methods.splitlines()

    def get_causes_list(self):
        return self.causes.splitlines()

    def get_recommended_actions_list(self):
        return self.recommended_actions.splitlines()

    def __str__(self):
        return self.title


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
