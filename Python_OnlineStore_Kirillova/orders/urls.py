from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Клиентские URL-ы
    path('checkout/', views.checkout, name='checkout'),
    path('history/', views.order_history, name='order_history'),
    path('detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
]