from django import forms
from django.core.validators import MinValueValidator
from products.models import Product
from .models import ShoppingCart


class AddToCartForm(forms.Form):
    """Форма для добавления товара в корзину"""
    product_id = forms.IntegerField(
        widget=forms.HiddenInput()  # Скрытое поле, передаём ID товара
    )
    quantity = forms.IntegerField(
        min_value=1,
        max_value=99,
        initial=1,
        label="Количество",
        validators=[MinValueValidator(1)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1,
            'max': 99
        })
    )

    def clean_product_id(self):
        """Проверка, что товар существует и активен"""
        product_id = self.cleaned_data.get('product_id')
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            return product
        except Product.DoesNotExist:
            raise forms.ValidationError("Товар не найден или недоступен")

    def clean(self):
        """Проверка доступного количества товара"""
        cleaned_data = super().clean()
        product = cleaned_data.get('product_id')
        quantity = cleaned_data.get('quantity')

        if product and quantity:
            if product.quantity < quantity:
                raise forms.ValidationError(
                    f"Недостаточно товара на складе. Доступно: {product.quantity} шт."
                )
        return cleaned_data


class UpdateCartForm(forms.Form):
    """Форма для обновления количества товара в корзине"""
    quantity = forms.IntegerField(
        min_value=1,
        max_value=99,
        validators=[MinValueValidator(1)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control quantity-input',
            'min': 1,
            'max': 99
        })
    )


class QuickAddToCartForm(forms.Form):
    """Быстрая форма для добавления в корзину (на странице товара)"""
    quantity = forms.IntegerField(
        min_value=1,
        max_value=99,
        initial=1,
        label="Количество",
        validators=[MinValueValidator(1)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1,
            'max': 99,
            'style': 'width: 80px; display: inline-block;'
        })
    )