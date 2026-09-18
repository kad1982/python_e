from datetime import timezone

from django.db import models


class User(models.Model):
    """Пользователь бота. Читает таблицу users, созданную SQLAlchemy."""
    id = models.BigIntegerField(primary_key=True)  # Telegram ID
    username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False  # ← Django НЕ создаёт и НЕ мигрирует
        db_table = "users"  # ← имя таблицы, которое создал бот
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        name = self.username or self.first_name or str(self.id)
        return f"{self.id} — {name}"


class Appointment(models.Model):
    """Встречи"""

    class Status(models.TextChoices):
        CONFIRMED = "confirmed", "Подтверждено"
        CANCELLED = "cancelled", "Отменено"
        PENDING = "pending", "Ожидается"

    event = models.ForeignKey(
        "events.Events",
        on_delete=models.CASCADE,
        related_name="appointments",
        verbose_name="Событие",
    )
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="organized_appointments",
        verbose_name="Организатор",
    )
    participants = models.ManyToManyField(
        User,
        related_name="participating_appointments",
        blank=True,
        verbose_name="Участники",
    )
    date = models.DateField()
    time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    details = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Статус",
    )

    class Meta:
        ordering = ["date", "time"]
        verbose_name = "Встреча"
        verbose_name_plural = "Встречи"
        indexes = [
            models.Index(fields=["organizer", "date"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return (
            f"#{self.id} — {self.event.name} — "
            f"{self.date} {self.time.strftime('%H:%M')} "
            f"[{self.get_status_display()}]"
        )

    @property
    def start_datetime(self):
        from datetime import datetime
        return datetime.combine(self.date, self.time)

    @property
    def end_datetime(self):
        from datetime import timedelta
        return self.start_datetime + timedelta(minutes=self.duration_minutes)


class ParticipantResponse(models.Model):
    """ Ответ участника на приглашение """

    class Choice(models.TextChoices):
        ACCEPTED = "accepted", "Принято"
        DECLINED = "declined", "Отклонено"
        PENDING = "pending", "Ожидает ответа"

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="responses",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="appointment_responses",
    )
    choice = models.CharField(
        max_length=20,
        choices=Choice.choices,
        default=Choice.PENDING,
    )
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("appointment", "user")
        verbose_name = "Ответ участника"
        verbose_name_plural = "Ответы участников"

    def __str__(self):
        return f"{self.user} → {self.appointment} [{self.get_choice_display()}]"
