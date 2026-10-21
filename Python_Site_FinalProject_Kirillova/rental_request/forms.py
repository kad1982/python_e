from django import forms
from .models import RentalRequest
from django.utils import timezone

class RentalRequestForm(forms.ModelForm):
    class Meta:
        model = RentalRequest
        fields = ['start_date', 'end_date', 'quantity', 'comment']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'comment': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Ваши пожелания или вопросы...'}),
        }

    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        if start_date and start_date < timezone.now().date():
            raise forms.ValidationError("Дата начала аренды не может быть в прошлом.")
        return start_date