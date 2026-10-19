from django.contrib import admin
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "place", "created_at")
    search_fields = ("name", "place")
    ordering = ("name",)
