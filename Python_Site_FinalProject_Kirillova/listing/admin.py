from django.contrib import admin
from .models import Listing


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "price", "location", "status", "created_at")
    list_filter = ("status", "location")
    search_fields = ("title", "description", "location")
    filter_horizontal = ("categories",)
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
