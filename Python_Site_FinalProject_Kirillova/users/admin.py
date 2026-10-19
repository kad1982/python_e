from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import Group

from .models import Users

# Скрыть встроенные Group из админки
admin.site.unregister(Group)


class UsersCreationForm(UserCreationForm):
    class Meta:
        model = Users
        fields = "__all__"


class UsersChangeForm(UserChangeForm):
    class Meta:
        model = Users
        fields = "__all__"


@admin.register(Users)
class UsersAdmin(UserAdmin):
    add_form = UsersCreationForm
    form = UsersChangeForm
    model = Users
    # Состав столбцов в списке пользователей
    list_display = (
        "username",
        "email",
        "last_name",
        "first_name",
        "status",
    )

    # Столбцы, по которым можно сортировать (клик по заголовку)
    list_display_links = ("username", "email")

    # Фильтры в правой панели
    list_filter = ("is_staff", "is_superuser", "is_active", "status")

    # Поля для поиска
    search_fields = ("username", "email", "last_name", "first_name", "phone")

    # Сортировка по умолчанию
    ordering = ("username",)

    # ---- Форма РЕДАКТИРОВАНИЯ ----
    fieldsets = (
        (None, {"fields": ("username", "password", "status",)}),
        ("Персональная информация", {
            "fields": ("last_name", "first_name", "middle_name", "email", "phone")
        }),
        ("Адрес", {
            "fields": ("country", "postal_code", "city", "street", "house_number", "apartment")
        }),
        ("Права", {
            "fields": ("is_active", "is_staff", "is_superuser",)
        }),
        ("Важные даты", {"fields": ("last_login", "created_at", "updated_at")}),
    )

    # Только для чтения — эти поля менять вручную нельзя
    readonly_fields = ("last_login", "created_at", "updated_at")

    # ---- Форма ДОБАВЛЕНИЯ ----
    add_fieldsets = (
        (None, {"fields": ("username", "password1", "password2", "status",)}),
        ("Персональная информация", {
            "fields": ("last_name", "first_name", "middle_name", "email", "phone")
        }),
        ("Адрес", {
            "fields": ("country", "postal_code", "city", "street", "house_number", "apartment")
        }),
        ("Права", {
            "fields": ("is_active", "is_staff", "is_superuser",)
        }),
    )
