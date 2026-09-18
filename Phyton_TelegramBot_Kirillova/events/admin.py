from django.contrib import admin
from .models import Events


@admin.register(Events)
class EventsAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user_id", "date", "time")
    list_filter = ("date",)
    search_fields = ("name", "details")
    date_hierarchy = "date"

    def has_add_permission(self, request): return False

    def has_change_permission(self, request, obj=None): return False

    def has_delete_permission(self, request, obj=None): return False
