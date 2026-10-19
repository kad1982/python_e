from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from rental_request.models import RentalRequest


class Transaction(models.Model):
    class TransactionStatus(models.IntegerChoices):
        PENDING = 0, "Ожидает оплаты"
        PAID = 1, "Оплачена"
        REFUNDED = 2, "Возврат"
        FAILED = 3, "Ошибка"

    rental_request = models.OneToOneField(
        RentalRequest,
        on_delete=models.PROTECT,
        related_name="transaction",
        verbose_name="Запрос на аренду",
    )
    payer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="transactions",
        verbose_name="Плательщик",
    )

    transaction_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата транзакции",
        db_index=True,
    )
    rental_start = models.DateField(
        verbose_name="Начало периода аренды",
        db_index=True,
    )
    rental_end = models.DateField(
        verbose_name="Конец периода аренды",
        db_index=True,
    )
    rental_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Стоимость аренды",
        db_index=True,
    )
    deposit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Залог",
    )

    status = models.IntegerField(
        choices=TransactionStatus,
        default=TransactionStatus.PENDING,
        verbose_name="Статус транзакции",
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transactions"
        verbose_name = "Транзакцию"
        verbose_name_plural = "Транзакции"
        ordering = ["-transaction_date"]
        indexes = [
            models.Index(fields=["status", "transaction_date"]),
            models.Index(fields=["payer", "status"]),
            models.Index(fields=["rental_start", "rental_end"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rental_end__gte=models.F("rental_start")),
                name="transaction_rental_end_gte_start",
            ),
            models.CheckConstraint(
                condition=models.Q(rental_cost__gte=0),
                name="transaction_cost_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(deposit__gte=0),
                name="transaction_deposit_non_negative",
            ),
        ]

    def __str__(self):
        return f"Транзакция #{self.pk} — {self.rental_cost}"