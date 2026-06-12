from django.contrib import admin
from .models import Farmer
from .models import SiteSettings

admin.site.register(SiteSettings)

admin.site.register(Farmer)