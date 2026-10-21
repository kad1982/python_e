from django.urls import path
from . import views

app_name = 'transaction'

urlpatterns = [
    # Список всех транзакций пользователя
    path('my/', views.MyTransactionsListView.as_view(), name='my_transactions'),

    # Создание (оплата) транзакции для конкретного одобренного запроса
    path('pay/<int:rental_request_pk>/', views.create_transaction, name='create_transaction'),

    # Детальный просмотр чека (опционально)
    path('<int:pk>/', views.TransactionDetailView.as_view(), name='transaction_detail'),
]