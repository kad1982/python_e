from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating_seller', 'rating_listing', 'comment']
        widgets = {
            'rating_seller': forms.Select(attrs={'class': 'form-select'}),
            'rating_listing': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Поделитесь впечатлениями о вещи и продавце...'}),
        }
        labels = {
            'rating_seller': 'Оценка продавца',
            'rating_listing': 'Оценка вещи',
            'comment': 'Ваш отзыв',
        }