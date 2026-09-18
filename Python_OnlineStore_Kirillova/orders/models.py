from django.db import models
from clients.models import Clients
from products.models import Product
from django.core.validators import MinValueValidator


# Create your models here.
class Order(models.Model):
    """Заказ"""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает обработки'
        PROCESSING = 'processing', 'В обработке'
        SHIPPED = 'shipped', 'Отправлен'
        DELIVERED = 'delivered', 'Доставлен'
        CANCELLED = 'cancelled', 'Отменён'
        REFUNDED = 'refunded', 'Возврат'

    client = models.ForeignKey(
        Clients,
        on_delete=models.PROTECT,
        verbose_name="Клиент",
        db_index=True
    )
    order_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата заказа",
        db_index=True
    )
    status = models.CharField(
        max_length=20,
        choices=Status,
        default=Status.PENDING,
        verbose_name="Статус",
        db_index=True
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Общая сумма",
        validators=[MinValueValidator(0)]
    )

    # Адрес доставки (копируем из профиля на момент заказа)
    shipping_street = models.CharField(max_length=100, verbose_name="Улица")
    shipping_house_number = models.CharField(max_length=10, verbose_name="Номер дома")
    shipping_apartment = models.CharField(max_length=10, verbose_name="Квартира", blank=True, null=True)
    shipping_city = models.CharField(max_length=50, verbose_name="Город")
    shipping_postal_code = models.CharField(max_length=20, verbose_name="Почтовый индекс")
    shipping_country = models.CharField(max_length=50, verbose_name="Страна", default="Россия")

    # Платёжная информация
    payment_method = models.CharField(
        max_length=50,
        verbose_name="Способ оплаты",
        blank=True,
        null=True
    )
    payment_status = models.CharField(
        max_length=50,
        verbose_name="Статус оплаты",
        default='pending'
    )

    # Трекинг
    tracking_number = models.CharField(
        max_length=100,
        verbose_name="Трек-номер",
        blank=True,
        null=True,
        db_index=True
    )
    delivered_at = models.DateTimeField(
        verbose_name="Дата доставки",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        db_table = 'orders'
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-order_date']
        indexes = [
            models.Index(fields=['client', 'status']),
            models.Index(fields=['order_date']),
        ]

    def __str__(self):
        return f"Заказ #{self.tracking_number} - {self.client} ({self.status})"


class OrderItem(models.Model):
    """Позиция в заказе"""
    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Заказ",
        db_index=True
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name="Товар",
        db_index=True
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Количество"
    )
    price_at_purchase = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена на момент покупки",
        validators=[MinValueValidator(0)]
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Сумма скидки",
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        db_table = 'order_items'
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'
        unique_together = ['order', 'product']  # В одном заказе товар может быть только один раз

    def __str__(self):
        return f"{self.order} - {self.product} x{self.quantity}"

    @property
    def subtotal(self):
        """Сумма позиции"""
        return self.price_at_purchase * self.quantity

    @property
    def total_with_discount(self):
        """Сумма со скидкой"""
        return self.subtotal - self.discount_amount
