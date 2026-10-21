from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import RentalRequest
from listing.models import Listing
from .forms import RentalRequestForm


class RentalRequestCreateView(LoginRequiredMixin, CreateView):
    """Создание запроса на аренду конкретной вещи"""
    model = RentalRequest
    form_class = RentalRequestForm
    template_name = 'rental_request/request_form.html'

    def dispatch(self, request, *args, **kwargs):
        # Получаем объявление, на которое кликнули
        self.listing = get_object_or_404(Listing, pk=self.kwargs['listing_pk'])

        # Нельзя арендовать свою же вещь
        if self.listing.author == request.user:
            messages.error(request, "Вы не можете арендовать собственную вещь.")
            return redirect('listing:listing_detail', pk=self.listing.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Автоматически привязываем арендатора и объявление
        form.instance.renter = self.request.user
        form.instance.listing = self.listing
        messages.success(self.request, 'Запрос на аренду успешно отправлен автору!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['listing'] = self.listing
        return context

    def get_success_url(self):
        return reverse_lazy('rental_request:my_requests')


class MyRequestsListView(LoginRequiredMixin, ListView):
    """Список аренд, которые запросил текущий пользователь (я арендатор)"""
    model = RentalRequest
    template_name = 'rental_request/my_requests.html'
    context_object_name = 'requests'
    paginate_by = 10

    def get_queryset(self):
        # Показываем только запросы текущего пользователя
        return RentalRequest.objects.filter(renter=self.request.user).order_by('-created_at')


class IncomingRequestsListView(LoginRequiredMixin, ListView):
    """Список входящих запросов на МОИ вещи (я арендодатель)"""
    model = RentalRequest
    template_name = 'rental_request/incoming_requests.html'
    context_object_name = 'requests'
    paginate_by = 10

    def get_queryset(self):
        # Показываем запросы, где автором объявления является текущий пользователь
        return RentalRequest.objects.filter(listing__author=self.request.user).order_by('-created_at')


class RentalRequestDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Детальный просмотр запроса (доступен только арендатору или арендодателю)"""
    model = RentalRequest
    template_name = 'rental_request/request_detail.html'
    context_object_name = 'request'

    def test_func(self):
        rental_request = self.get_object()
        # Доступ даём только тому, кто запрашивает, и владельцу вещи
        return self.request.user == rental_request.renter or self.request.user == rental_request.listing.author


class RentalRequestUpdateStatusView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Изменение статуса запроса (Одобрить / Отклонить).
    Доступно только владельцу объявления.
    """
    model = RentalRequest
    fields = ['status']  # Разрешаем менять только статус
    template_name = 'rental_request/request_status_form.html'

    def test_func(self):
        rental_request = self.get_object()
        return self.request.user == rental_request.listing.author

    def form_valid(self, form):
        messages.success(self.request, 'Статус запроса обновлён.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('rental_request:incoming_requests')