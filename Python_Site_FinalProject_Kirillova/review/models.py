from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from listing.models import Listing
from rental_request.models import RentalRequest


class Review(models.Model):
    # Привязываем отзыв к конкретной аренде
    rental_request = models.OneToOneField(
        RentalRequest,
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name="Запрос на аренду"
    )
    # Автор отзыва (арендатор)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_written',
        verbose_name="Автор отзыва"
    )
    # Кому оставляют отзыв (владелец вещи)
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_received',
        verbose_name="Продавец (владелец вещи)"
    )
    # Объявление
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="Объявление"
    )

    # Оценки (от 1 до 5)
    rating_seller = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Оценка продавца"
    )
    rating_listing = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Оценка вещи"
    )

    comment = models.TextField(verbose_name="Текст отзыва")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Отзыв от {self.author.username} на {self.listing.title}"