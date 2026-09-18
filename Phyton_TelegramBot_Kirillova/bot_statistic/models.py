from django.db import models


class BotStatistics(models.Model):
    id = models.BigIntegerField(primary_key=True)
    date = models.DateField()
    user_count = models.IntegerField(default=0)
    event_count = models.IntegerField(default=0)
    edited_events = models.IntegerField(default=0)
    cancelled_events = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = "bot_statistics"
        ordering = ["-date"]
        verbose_name = "Статистика бота"
        verbose_name_plural = "Статистика бота"

    def __str__(self):
        return f"{self.date} — users={self.user_count}, events={self.event_count}"