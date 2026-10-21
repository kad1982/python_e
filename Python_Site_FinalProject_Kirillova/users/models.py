from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.core.validators import RegexValidator


class UserStatus(models.IntegerChoices):
    INACTIVE = 0, "Не активен"
    ACTIVE = 1, "Активен"


class UsersManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("Логин обязателен")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("status", UserStatus.ACTIVE)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")

        return self.create_user(username, password, **extra_fields)


class Users(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True, verbose_name="Логин", )
    # ФИО
    last_name = models.CharField(max_length=50, verbose_name="Фамилия", db_index=True)
    first_name = models.CharField(max_length=50, verbose_name="Имя", db_index=True)
    middle_name = models.CharField(
        max_length=50, verbose_name="Отчество", blank=True, null=True
    )

    status = models.IntegerField(
        choices=UserStatus,
        default=UserStatus.ACTIVE,
        verbose_name="Тэг статуса пользователя",
    )

    # Контактная информация
    email = models.EmailField(
        max_length=100,
        blank=True, null=True,
        verbose_name="Email",
        db_index=True,
    )
    phone = models.CharField(
        max_length=20,
        verbose_name="Телефон",
        db_index=True,
        validators=[
            RegexValidator(
                regex=r'^\+?[0-9]{10,15}$',
                message="Телефон должен быть в формате: +71234567890 (10-15 цифр)",
            )
        ],
    )

    # Адрес
    street = models.CharField(max_length=100, verbose_name="Улица")
    house_number = models.CharField(max_length=10, verbose_name="Номер дома")
    apartment = models.CharField(
        max_length=10, verbose_name="Квартира", blank=True, null=True
    )
    city = models.CharField(max_length=50, verbose_name="Город", db_index=True)
    postal_code = models.CharField(max_length=20, verbose_name="Почтовый индекс")
    country = models.CharField(max_length=50, verbose_name="Страна", default="Russia")

    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_staff = models.BooleanField(default=False, verbose_name="Доступ к админке")
    is_superuser = models.BooleanField(default=False, verbose_name="Cуперузер")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    USERNAME_FIELD = "username"

    REQUIRED_FIELDS = []

    objects = UsersManager()

    class Meta:
        db_table = "users"
        verbose_name = "Пользователя"
        verbose_name_plural = "Пользователи"
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["last_name", "first_name"]),
            models.Index(fields=["city"]),
        ]

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name or ''}".strip()

    def get_full_name(self):
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return " ".join(parts)

    def get_short_name(self):
        return self.first_name

    @property
    def full_name(self):
        return self.get_full_name()

    @property
    def full_address(self):
        parts = [self.postal_code, self.city, self.street, self.house_number]
        if self.apartment:
            parts.append(f"кв. {self.apartment}")
        parts.append(self.country)
        return ", ".join(parts)
