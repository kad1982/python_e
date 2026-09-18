from django.db import models
from django.core.validators import MinValueValidator
from clients.models import Clients
from products.models import Product

# Create your models here.
class ShoppingCart(models.Model):
    """Корзина покупок"""
    client = models.ForeignKey(
        Clients,
        on_delete=models.CASCADE,
        verbose_name="Клиент",
        db_index=True
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Товар",
        db_index=True
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Количество"
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата добавления"
    )

    class Meta:
        db_table = 'shopping_cart'
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        unique_together = ['client', 'product']  # Один товар в корзине у клиента может быть только один раз
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.client} - {self.product} x {self.quantity}"

    @property
    def total_price(self):
        """Общая стоимость позиции в корзине"""
        return self.product.price * self.quantity