from django.contrib import admin
from .models import BotStatistics


@admin.register(BotStatistics)
class BotStatisticsAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "user_count",
        "event_count",
        "edited_events",
        "cancelled_events",
    )
    list_filter = ("date",)
    search_fields = ("date",)
    ordering = ("-date",)

    # Делаем модель read-only
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False