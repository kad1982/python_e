from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    parent = models.ForeignKey('self', on_delete=models.PROTECT, verbose_name="Родительская категория", null=True,
                               blank=True)

    class Meta:
        db_table = 'products_category'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(blank=True, null=True,verbose_name="Описание")
    price = models.DecimalField(default=0.00, max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to='products', null=True, blank=True, verbose_name="Изображение")
    category = models.ForeignKey('Category', on_delete=models.PROTECT, db_index=True, verbose_name="Категория")
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name="Количество")
    discount = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)],
                                   verbose_name="Скидка")

    class Meta:
        db_table = 'products_product'
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return self.name

    def sell_price(self):
        if self.discount:
            return round(self.price - self.price * self.discount / 100, 2)

        return self.price


