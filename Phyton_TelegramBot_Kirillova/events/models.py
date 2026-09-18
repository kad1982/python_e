from django.db import models

class Events(models.Model):
    id = models.BigIntegerField(primary_key=True)
    user_id = models.ForeignKey(
        "appointment.User",
        db_column="user_id",
        on_delete=models.CASCADE,
        related_name="events",
    )
    name = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    details = models.TextField()
    is_public = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = "calendar"
        ordering = ["-date", "-time"]
        verbose_name = "Заметка"
        verbose_name_plural = "Заметки"

    def __str__(self):
        return f"#{self.id} — {self.name} ({self.date} {self.time})"
