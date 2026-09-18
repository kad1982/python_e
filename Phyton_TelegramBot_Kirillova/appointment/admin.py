from django.contrib import admin

from appointment.models import Appointment, User, ParticipantResponse


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "first_name", "last_name")
    search_fields = ("id", "username", "first_name", "last_name")

    def has_add_permission(self, request): return False

    def has_change_permission(self, request, obj=None): return False

    def has_delete_permission(self, request, obj=None): return False


class ParticipantResponseInline(admin.TabularInline):
    model = ParticipantResponse
    extra = 0
    readonly_fields = ("user", "choice", "responded_at")
    can_delete = False

    def has_add_permission(self, request, obj=None): return False


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "id", "event", "organizer", "date", "time",
        "duration_minutes", "participants_count",
    )
    list_filter = ("status", "date", "organizer")
    search_fields = ("event__name", "details")
    date_hierarchy = "date"
    filter_horizontal = ("participants",)
    autocomplete_fields = ("event", "organizer")
    inlines = [ParticipantResponseInline]
    ordering = ("-date", "-time")

    @admin.display(description="Статус", ordering="status")
    @admin.display(description="Участников")
    def participants_count(self, obj):
        return obj.participants.count()


@admin.register(ParticipantResponse)
class ParticipantResponseAdmin(admin.ModelAdmin):
    list_display = ("id", "appointment", "user", "choice", "responded_at")
    list_filter = ("choice",)
    search_fields = ("appointment__event__name", "user__id")
