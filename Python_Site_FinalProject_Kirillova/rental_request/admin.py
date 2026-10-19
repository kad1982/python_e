from django.contrib import admin
from .models import RentalRequest


@admin.register(RentalRequest)
class RentalRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "renter", "start_date", "end_date",
                    "quantity", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("listing__title", "renter__username")
    ordering = ("-created_at",)
    date_hierarchy = "start_date"
