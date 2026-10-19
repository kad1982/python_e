from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from category.models import Category


class Listing(models.Model):
    class ListingStatus(models.IntegerChoices):
        DRAFT = 0, "Черновик"
        PUBLISHED = 1, "Опубликовано"
        ARCHIVED = 2, "В архиве"

    title = models.CharField(
        max_length=200,
        verbose_name="Название",
        db_index=True,
    )
    description = models.TextField(
        verbose_name="Описание",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Цена за период",
        db_index=True,
    )
    location = models.CharField(
        max_length=200,
        verbose_name="Местоположение",
        db_index=True,
    )
    available_from = models.DateField(
        verbose_name="Доступно с",
        db_index=True,
    )
    available_to = models.DateField(
        verbose_name="Доступно по",
        db_index=True,
    )

    # Контакты автора объявления
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="listings",
        verbose_name="Автор",
    )
    contact_phone = models.CharField(
        max_length=20,
        verbose_name="Контактный телефон",
    )
    contact_email = models.EmailField(
        verbose_name="Контактный email",
    )

    status = models.IntegerField(
        choices=ListingStatus,
        default=ListingStatus.DRAFT,
        verbose_name="Статус объявления",
        db_index=True,
    )

    categories = models.ManyToManyField(
        Category,
        related_name="listings",
        blank=True,
        verbose_name="Категории",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "listings"
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering = ["-created_at"]
        indexes = [
            # Частые фильтры: "опубликованные объявления в городе"
            models.Index(fields=["status", "location"]),
            # Фильтр по цене в пределах категории/города
            models.Index(fields=["location", "price"]),
            # Пересечение дат аренды
            models.Index(fields=["available_from", "available_to"]),
            # Объявления автора
            models.Index(fields=["author", "status"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(available_to__gte=models.F("available_from")),
                name="listing_available_to_gte_from",
            ),
            models.CheckConstraint(
                condition=models.Q(price__gte=0),
                name="listing_price_non_negative",
            ),
        ]

    def __str__(self):
        return self.title
