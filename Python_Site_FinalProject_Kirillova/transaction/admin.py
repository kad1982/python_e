from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "rental_request", "payer", "rental_cost",
                    "transaction_date", "status")
    list_filter = ("status",)
    search_fields = ("rental_request__id", "payer__username")
    ordering = ("-transaction_date",)
    date_hierarchy = "transaction_date"
