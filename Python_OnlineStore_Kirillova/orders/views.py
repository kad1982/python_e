from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.core.paginator import Paginator

from .models import Order, OrderItem
from .forms import SimpleOrderForm
from shopping_carts.models import ShoppingCart


@login_required
@transaction.atomic
def checkout(request):
    try:
        client = request.user.client
    except AttributeError:
        messages.error(request, "Профиль клиента не найден")
        return redirect('products:product_list')

    # Получаем товары из корзины
    cart_items = ShoppingCart.objects.filter(client=client).select_related('product')

    if not cart_items.exists():
        messages.error(request, "Корзина пуста")
        return redirect('shopping_carts:cart_view')

    # Проверяем наличие товаров на складе
    for item in cart_items:
        if item.quantity > item.product.quantity:
            messages.error(
                request,
                f"Недостаточно товара '{item.product.name}'. Доступно: {item.product.quantity} шт."
            )
            return redirect('shopping_carts:cart_view')

    if request.method == 'POST':
        form = SimpleOrderForm(request.POST)
        if form.is_valid():
            # Вычисляем общую сумму
            total_amount = sum(item.total_price for item in cart_items)

            # Разбираем адрес
            address_parts = form.cleaned_data['address'].split(',')
            street = address_parts[0].strip() if len(address_parts) > 0 else ''
            city = address_parts[1].strip() if len(address_parts) > 1 else ''
            house_number = address_parts[2].strip() if len(address_parts) > 2 else ''

            # Создаём заказ
            order = Order.objects.create(
                client=client,
                total_amount=total_amount,
                shipping_street=street or 'Не указано',
                shipping_house_number=house_number or 'Не указано',
                shipping_city=city or 'Не указано',
                shipping_postal_code='000000',
                shipping_country='Russia',
                payment_method='cash',  # По умолчанию наличные
                status=Order.Status.PENDING,
            )

            # Создаём позиции заказа
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price_at_purchase=cart_item.product.price,
                    discount_amount=0,
                )

                # Уменьшаем количество товара на складе
                product = cart_item.product
                product.quantity -= cart_item.quantity
                product.save()

            # Очищаем корзину
            cart_items.delete()

            messages.success(request, f"Заказ #{order.id} успешно оформлен!")
            return redirect('orders:order_detail', order_id=order.id)
    else:
        form = SimpleOrderForm()

    context = {
        'form': form,
        'cart_items': cart_items,
        'total': sum(item.total_price for item in cart_items),
        'total_items': sum(item.quantity for item in cart_items),
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def order_detail(request, order_id):
    """Просмотр деталей заказа"""
    try:
        client = request.user.client
    except AttributeError:
        messages.error(request, "Профиль клиента не найден")
        return redirect('products:product_list')

    order = get_object_or_404(Order, id=order_id, client=client)
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def order_history(request):
    """История заказов"""
    try:
        client = request.user.client
    except AttributeError:
        messages.error(request, "Профиль клиента не найден")
        return render(request, 'orders/order_history.html', {
            'orders': [],
            'no_auth': True
        })

    orders = Order.objects.filter(client=client).order_by('-order_date')

    # Пагинация
    paginator = Paginator(orders, 10)  # 10 заказов на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'orders': page_obj,
    }
    return render(request, 'orders/order_history.html', context)

@login_required
def cancel_order(request, order_id):
    """Отмена заказа (до его отправки)"""
    try:
        client = request.user.client
    except AttributeError:
        messages.error(request, "Профиль клиента не найден")
        return redirect('products:product_list')

    order = get_object_or_404(Order, id=order_id, client=client)

    # Проверяем, можно ли отменить заказ
    if order.status in [Order.Status.DELIVERED, Order.Status.SHIPPED]:
        messages.error(request, "Невозможно отменить заказ, который уже отправлен или доставлен")
        return redirect('orders:order_detail', order_id=order.id)

    if order.status == Order.Status.CANCELLED:
        messages.warning(request, "Заказ уже был отменён")
        return redirect('orders:order_detail', order_id=order.id)

    if request.method == 'POST':
        with transaction.atomic():
            # Возвращаем товары на склад
            for item in order.items.all():
                product = item.product
                product.quantity += item.quantity
                product.save()

            # Меняем статус заказа
            order.status = Order.Status.CANCELLED
            order.save()

        messages.success(request, f"Заказ #{order.id} отменён")
        return redirect('orders:order_history')

    return render(request, 'orders/cancel_order.html', {'order': order})

