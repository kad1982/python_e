from django import forms
from .models import Listing
from django.utils import timezone


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = [
            'image', 'title', 'description', 'price', 'location',
            'available_from', 'available_to', 'categories',
            'contact_phone', 'contact_email',
            'status'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'available_from': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'available_to': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'categories': forms.CheckboxSelectMultiple(),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_available_from(self):
        available_from = self.cleaned_data.get('available_from')
        if available_from and available_from < timezone.now().date():
            raise forms.ValidationError("Дата начала сдачи вещи не может быть в прошлом.")
        return available_from

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ограничиваем выбор статусов для пользователя
        self.fields['status'].choices = [
            (Listing.ListingStatus.DRAFT, "Черновик"),
            (Listing.ListingStatus.PENDING, "Отправить на модерацию"),
        ]
