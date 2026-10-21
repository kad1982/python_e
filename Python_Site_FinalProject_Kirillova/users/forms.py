from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Users


# Форма для регистрации
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Users
        # Перечисляем поля, которые должны быть при регистрации
        fields = ('username',)


# Форма для редактирования профиля
class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = Users
        fields = ('last_name', 'first_name', 'middle_name', 'email', 'phone',
                  'country', 'postal_code', 'city', 'street', 'house_number', 'apartment')

        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'street': forms.TextInput(attrs={'class': 'form-control'}),
            'house_number': forms.TextInput(attrs={'class': 'form-control'}),
            'apartment': forms.TextInput(attrs={'class': 'form-control'}),
        }