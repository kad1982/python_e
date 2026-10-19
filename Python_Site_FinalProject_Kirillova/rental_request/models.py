from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from listing.models import Listing


class RentalRequest(models.Model):
    class RequestStatus(models.IntegerChoices):
        PENDING = 0, "Ожидает"
        APPROVED = 1, "Одобрен"
        REJECTED = 2, "Отклонён"
        CANCELLED = 3, "Отменён"

    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="rental_requests",
        verbose_name="Объявление",
    )
    renter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rental_requests",
        verbose_name="Арендатор",
    )

    start_date = models.DateField(
        verbose_name="Дата начала",
        db_index=True,
    )
    end_date = models.DateField(
        verbose_name="Дата окончания",
        db_index=True,
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Количество предметов",
    )
    comment = models.TextField(
        blank=True,
        verbose_name="Комментарий",
    )

    status = models.IntegerField(
        choices=RequestStatus,
        default=RequestStatus.PENDING,
        verbose_name="Статус запроса",
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "rental_requests"
        verbose_name = "Запрос на аренду"
        verbose_name_plural = "Запросы на аренду"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["listing", "status"]),
            models.Index(fields=["renter", "status"]),
            models.Index(fields=["start_date", "end_date"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_date__gte=models.F("start_date")),
                name="rental_request_end_gte_start",
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gte=1),
                name="rental_request_quantity_positive",
            ),
            # Один арендатор не может дважды запросить одно объявление
            # на одинаковый период (опционально — можно убрать).
            models.UniqueConstraint(
                fields=["listing", "renter", "start_date", "end_date"],
                name="unique_rental_request_per_period",
            ),
        ]

    def __str__(self):
        return f"Запрос #{self.pk} на {self.listing}"
