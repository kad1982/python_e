from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal

from .models import Transaction
from rental_request.models import RentalRequest


class MyTransactionsListView(LoginRequiredMixin, ListView):
    """Список транзакций текущего пользователя"""
    model = Transaction
    template_name = 'transaction/my_transactions.html'
    context_object_name = 'transactions'
    paginate_by = 10

    def get_queryset(self):
        return Transaction.objects.filter(payer=self.request.user).order_by('-transaction_date')


class TransactionDetailView(LoginRequiredMixin, DetailView):
    """Просмотр деталей транзакции (чека)"""
    model = Transaction
    template_name = 'transaction/transaction_detail.html'
    context_object_name = 'transaction'

    def get_queryset(self):
        # Разрешаем смотреть только свои транзакции
        return Transaction.objects.filter(payer=self.request.user)


@login_required
def create_transaction(request, rental_request_pk):
    """Создание транзакции (имитация оплаты)"""
    rental_request = get_object_or_404(RentalRequest, pk=rental_request_pk)

    # Проверки безопасности
    if rental_request.renter != request.user:
        messages.error(request, "Вы не можете оплатить чужой запрос.")
        return redirect('rental_request:my_requests')

    if rental_request.status != RentalRequest.RequestStatus.APPROVED:
        messages.error(request, "Оплатить можно только одобренный запрос.")
        return redirect('rental_request:request_detail', pk=rental_request.pk)

    # Проверяем, нет ли уже транзакции для этого запроса
    if hasattr(rental_request, 'transaction'):
        messages.info(request, "Этот запрос уже оплачен.")
        return redirect('transaction:transaction_detail', pk=rental_request.transaction.pk)

    # Рассчитываем стоимость
    # (Для простоты берем цену объявления * количество дней)
    days = (rental_request.end_date - rental_request.start_date).days
    if days == 0:
        days = 1  # Минимум 1 сутки

    base_cost = rental_request.listing.price * days * rental_request.quantity
    deposit = Decimal('5000.00')  # Фиксированный залог (можно брать из модели Listing, если добавите)

    if request.method == 'POST':
        # Создаем транзакцию
        transaction = Transaction.objects.create(
            rental_request=rental_request,
            payer=request.user,
            rental_start=rental_request.start_date,
            rental_end=rental_request.end_date,
            rental_cost=base_cost,
            deposit=deposit,
            status=Transaction.TransactionStatus.PAID  # Имитируем успешную оплату
        )

        messages.success(request, "Оплата прошла успешно! Вещь забронирована.")
        return redirect('transaction:transaction_detail', pk=transaction.pk)

    # Если GET-запрос, показываем страницу подтверждения оплаты
    context = {
        'rental_request': rental_request,
        'days': days,
        'base_cost': base_cost,
        'deposit': deposit,
        'total_cost': base_cost + deposit
    }
    return render(request, 'transaction/payment_checkout.html', context)