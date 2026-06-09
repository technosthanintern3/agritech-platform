from django.contrib import admin
from .models import Crop, SeedVariety, Review

admin.site.register(Crop)
admin.site.register(SeedVariety)
admin.site.register(Review)