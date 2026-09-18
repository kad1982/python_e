from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction, models
from django.http import JsonResponse
from django.urls import reverse

from .models import ShoppingCart
from .forms import AddToCartForm, UpdateCartForm, QuickAddToCartForm
from products.models import Product

@login_required
def quick_add_to_cart(request, product_id):
    """Быстрое добавление товара в корзину (AJAX или прямой запрос)"""
    product = get_object_or_404(Product, id=product_id)
    client = request.user.client

    if request.method == 'POST':
        form = QuickAddToCartForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']

            if quantity > product.quantity:
                messages.error(request, f"Недостаточно товара. Доступно: {product.quantity} шт.")
                return redirect('products:product_detail', pk=product_id)

            cart_item, created = ShoppingCart.objects.get_or_create(
                client=client,
                product=product,
                defaults={'quantity': quantity}
            )

            if not created:
                new_quantity = cart_item.quantity + quantity
                if new_quantity <= product.quantity:
                    cart_item.quantity = new_quantity
                    cart_item.save()
                else:
                    messages.error(request, f"Недостаточно товара. Доступно: {product.quantity} шт.")
                    return redirect('products:product_detail', pk=product_id)

            messages.success(request, f"Товар '{product.name}' добавлен в корзину!")
            return redirect('shopping_carts:cart_view')
    else:
        form = QuickAddToCartForm()

    return render(request, 'shopping_carts/quick_add.html', {
        'form': form,
        'product': product
    })


@login_required
def cart_view(request):
    """Просмотр корзины"""
    try:
        client = request.user.client
    except AttributeError:
        messages.error(request, "Профиль клиента не найден")
        return render(request, 'shopping_carts/cart_view.html', {
            'cart_items': [],
            'total': 0,
            'total_items': 0,
            'no_auth': True
        })

    cart_items = ShoppingCart.objects.filter(client=client).select_related('product')

    # Проверяем наличие товаров на складе
    for item in cart_items:
        if item.quantity > item.product.quantity:
            messages.warning(
                request,
                f"Товара '{item.product.name}' осталось только {item.product.quantity} шт. "
                f"Ваше количество в корзине: {item.quantity} шт."
            )

    total = sum(item.total_price for item in cart_items)
    total_items = sum(item.quantity for item in cart_items)

    context = {
        'cart_items': cart_items,
        'total': total,
        'total_items': total_items,
    }
    return render(request, 'shopping_carts/cart_view.html', context)


@login_required
def update_cart_item(request, item_id):
    """Обновление количества товара в корзине"""
    try:
        client = request.user.client
    except AttributeError:
        messages.error(request, "Профиль клиента не найден")
        return redirect('products:product_list')

    cart_item = get_object_or_404(ShoppingCart, id=item_id, client=client)

    if request.method == 'POST':
        form = UpdateCartForm(request.POST)
        if form.is_valid():
            new_quantity = form.cleaned_data['quantity']

            if new_quantity <= cart_item.product.quantity:
                cart_item.quantity = new_quantity
                cart_item.save()
                messages.success(request, "Количество обновлено")
            else:
                messages.error(
                    request,
                    f"Недостаточно товара. Доступно: {cart_item.product.quantity} шт."
                )
        else:
            messages.error(request, "Пожалуйста, введите корректное количество")

    return redirect('shopping_carts:cart_view')


@login_required
def remove_from_cart(request, item_id):
    """Удаление товара из корзины"""
    try:
        client = request.user.client
    except AttributeError:
        messages.error(request, "Профиль клиента не найден")
        return redirect('products:product_list')

    cart_item = get_object_or_404(ShoppingCart, id=item_id, client=client)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f"Товар '{product_name}' удалён из корзины")
    return redirect('shopping_carts:cart_view')


@login_required
def clear_cart(request):
    """Очистка всей корзины"""
    try:
        client = request.user.client
    except AttributeError:
        messages.error(request, "Профиль клиента не найден")
        return redirect('products:product_list')

    if request.method == 'POST':
        count = ShoppingCart.objects.filter(client=client).delete()[0]
        messages.success(request, f"Корзина очищена. Удалено {count} товаров.")
    else:
        messages.warning(request, "Для очистки корзины используйте форму")

    return redirect('shopping_carts:cart_view')


@login_required
def cart_count(request):
    """AJAX-запрос для получения количества товаров в корзине"""
    try:
        client = request.user.client
        count = ShoppingCart.objects.filter(client=client).count()
        total_items = ShoppingCart.objects.filter(client=client).aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
    except AttributeError:
        count = 0
        total_items = 0

    return JsonResponse({
        'count': count,
        'total_items': total_items
    })