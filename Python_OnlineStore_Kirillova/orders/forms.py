from django import forms
from django.core.exceptions import ValidationError
from shopping_carts.models import ShoppingCart


class SimpleOrderForm(forms.Form):
    """Простая форма для быстрого оформления заказа (из вашего примера)"""
    name = forms.CharField(
        max_length=255,
        label="Ваше имя",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванов Иван Иванович'})
    )
    address = forms.CharField(
        max_length=500,
        label="Адрес доставки",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'г. Москва, ул. Ленина, д. 10, кв. 5'})
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@mail.ru'})
    )
    # Поле для выбора товаров из корзины (можно использовать для быстрого добавления)
    cart = forms.ModelChoiceField(
        queryset=ShoppingCart.objects.all(),
        label="Выберите товар из корзины",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def clean_name(self):
        """Проверка, что имя не пустое"""
        name = self.cleaned_data.get('name')
        if not name.strip():
            raise ValidationError("Имя не может быть пустым")
        return name.strip()
