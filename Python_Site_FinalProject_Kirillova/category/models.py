from django.db import models


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Название",
        db_index=True,
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
    )
    place = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Место/происхождение",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "categories"
        verbose_name = "Категорию"
        verbose_name_plural = "Категории"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name
