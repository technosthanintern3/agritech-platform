from django.contrib import admin

from .models import Crop, SeedVariety, Review


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
	search_fields = ('name',)


@admin.register(SeedVariety)
class SeedVarietyAdmin(admin.ModelAdmin):
	list_display = ('name', 'crop', 'price')
	search_fields = ('name', 'crop__name')
	list_filter = ('crop',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
	list_display = ('product', 'name', 'rating', 'is_hidden', 'created_at')
	list_filter = ('is_hidden', 'rating', 'product')
	search_fields = ('name', 'review_text', 'product__name', 'farmer__name')
	actions = ['hide_reviews', 'unhide_reviews']

	def hide_reviews(self, request, queryset):
		queryset.update(is_hidden=True)

	def unhide_reviews(self, request, queryset):
		queryset.update(is_hidden=False)