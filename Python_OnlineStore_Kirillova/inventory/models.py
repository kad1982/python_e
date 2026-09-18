from django.db import models
from products.models import Product

# Create your models here.
class Inventory(models.Model):
    """Запасы на складе"""
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Товар",
        related_name='inventory',
        db_index=True
    )
    quantity = models.PositiveIntegerField(
        default=0,
        verbose_name="Количество на складе"
    )
    reserved_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name="Зарезервировано"
    )
    warehouse_location = models.CharField(
        max_length=100,
        verbose_name="Местоположение на складе",
        blank=True,
        null=True
    )
    last_restocked_date = models.DateTimeField(
        verbose_name="Дата последнего пополнения",
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        db_table = 'inventory'
        verbose_name = 'Запас'
        verbose_name_plural = 'Запасы'

    def __str__(self):
        return f"{self.product} - {self.quantity} шт."

    @property
    def available_quantity(self):
        """Доступное количество"""
        return self.quantity - self.reserved_quantity