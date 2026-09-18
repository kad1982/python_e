from django.db import models
from django.core.validators import RegexValidator
from django.conf import settings


# Create your models here.

class Clients(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_profile'
    )
    # ФИО
    last_name = models.CharField(
        max_length=50,
        verbose_name="Фамилия",
        db_index=True
    )
    first_name = models.CharField(
        max_length=50,
        verbose_name="Имя",
        db_index=True
    )
    middle_name = models.CharField(
        max_length=50,
        verbose_name="Отчество",
        blank=True,
        null=True
    )

    # Контактная информация
    email = models.EmailField(
        max_length=100,
        unique=True,
        verbose_name="Email",
        db_index=True,
        error_messages={
            'unique': "Пользователь с таким email уже зарегистрирован",
        }
    )
    phone = models.CharField(
        max_length=20,
        verbose_name="Телефон",
        db_index=True,
        validators=[
            RegexValidator(
                regex=r'^\+?[0-9]{10,15}$',
                message="Телефон должен быть в формате: +71234567890 (10-15 цифр)"
            )
        ]
    )

    # Адрес
    street = models.CharField(
        max_length=100,
        verbose_name="Улица"
    )
    house_number = models.CharField(
        max_length=10,
        verbose_name="Номер дома"
    )
    apartment = models.CharField(
        max_length=10,
        verbose_name="Квартира",
        blank=True,
        null=True
    )
    city = models.CharField(
        max_length=50,
        verbose_name="Город",
        db_index=True
    )
    postal_code = models.CharField(
        max_length=20,
        verbose_name="Почтовый индекс"
    )
    country = models.CharField(
        max_length=50,
        verbose_name="Страна",
        default="Russia"
    )

    # Временные метки
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата регистрации"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        db_table = 'clients'
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['city']),
        ]

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name or ''}".strip()

    @property
    def full_name(self):
        """Полное ФИО"""
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return " ".join(parts)

    @property
    def full_address(self):
        """Полный адрес"""
        parts = [self.postal_code, self.city, self.street, self.house_number]
        if self.apartment:
            parts.append(f"кв. {self.apartment}")
        parts.append(self.country)
        return ", ".join(parts)