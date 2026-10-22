from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from rental_request.models import RentalRequest
from .models import Review
from .forms import ReviewForm


class AddReviewView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'review/add_review.html'

    def dispatch(self, request, *args, **kwargs):
        # Получаем запрос на аренду
        self.rental_request = get_object_or_404(RentalRequest, pk=self.kwargs['request_pk'])

        # Проверяем: отзыв может оставить только арендатор, и только если статус "Одобрен" (или "Опубликовано", если у вас транзакции)
        if self.rental_request.renter != request.user:
            messages.error(request, "Вы не можете оставить отзыв на чужую аренду.")
            return redirect('rental_request:my_requests')

        if self.rental_request.status != RentalRequest.RequestStatus.APPROVED:
            messages.error(request, "Оставить отзыв можно только после завершения аренды.")
            return redirect('rental_request:my_requests')

        # Проверяем, не оставлял ли он уже отзыв
        if hasattr(self.rental_request, 'review'):
            messages.info(request, "Вы уже оставили отзыв по этой аренде.")
            return redirect('listing:listing_detail', pk=self.rental_request.listing.pk)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.seller = self.rental_request.listing.author
        form.instance.listing = self.rental_request.listing
        form.instance.rental_request = self.rental_request

        messages.success(self.request, 'Спасибо за ваш отзыв!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('listing:listing_detail', kwargs={'pk': self.rental_request.listing.pk})