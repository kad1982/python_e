from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .models import Clients
from django.contrib.auth import logout


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('profile_edit')  # Перенаправляем на заполнение профиля
    else:
        form = UserCreationForm()
    return render(request, 'clients/register.html', {'form': form})


def home_view(request):
    return render(request, 'home.html')

@login_required
def custom_logout(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Вы успешно вышли из системы.')
    else:
        # Для GET-запросов тоже разрешаем выход (небезопасно!)
        logout(request)
        messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('homepage:index')

@login_required
def profile_view(request):
    try:
        client = Clients.objects.get(user=request.user)
    except Clients.DoesNotExist:
        client = None
        messages.warning(request, 'Пожалуйста, заполните свой профиль.')

    context = {
        'user': request.user,
        'client': client,
    }
    return render(request, 'clients/profile.html', context)

@login_required
def my_profile(request):
    try:
        client = Clients.objects.get(user=request.user)
        return redirect('clients_detail', pk=client.pk)
    except Clients.DoesNotExist:
        messages.warning(request, 'Профиль клиента не найден. Заполните данные профиля.')
        return redirect('profile_edit')


@login_required
def profile_edit(request):
    try:
        client = Clients.objects.get(user=request.user)
    except Clients.DoesNotExist:
        client = None

    if request.method == 'POST':
        user = request.user

        # Обновляем данные пользователя (если они есть в модели User)
        # Но у вас ФИО хранятся в Clients, поэтому не обновляем User

        # Создаем или обновляем клиента
        if client:
            # Обновляем существующего клиента
            client.last_name = request.POST.get('last_name', client.last_name)
            client.first_name = request.POST.get('first_name', client.first_name)
            client.middle_name = request.POST.get('middle_name', client.middle_name)
            client.email = request.POST.get('email', client.email)
            client.phone = request.POST.get('phone', client.phone)
            client.street = request.POST.get('street', client.street)
            client.house_number = request.POST.get('house_number', client.house_number)
            client.apartment = request.POST.get('apartment', client.apartment)
            client.city = request.POST.get('city', client.city)
            client.postal_code = request.POST.get('postal_code', client.postal_code)
            client.country = request.POST.get('country', client.country)
            client.save()
            messages.success(request, 'Профиль успешно обновлен!')
        else:
            # Создаем нового клиента
            client = Clients.objects.create(
                user=user,
                last_name=request.POST.get('last_name', ''),
                first_name=request.POST.get('first_name', ''),
                middle_name=request.POST.get('middle_name', ''),
                email=request.POST.get('email', ''),
                phone=request.POST.get('phone', ''),
                street=request.POST.get('street', ''),
                house_number=request.POST.get('house_number', ''),
                apartment=request.POST.get('apartment', ''),
                city=request.POST.get('city', ''),
                postal_code=request.POST.get('postal_code', ''),
                country=request.POST.get('country', 'Russia'),
            )
            messages.success(request, 'Профиль успешно создан!')

        return redirect('profile')

    context = {
        'user': request.user,
        'client': client,
    }
    return render(request, 'clients/profile_edit.html', context)


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Важно! Чтобы не разлогинивать
            messages.success(request, 'Пароль успешно изменен!')
            return redirect('profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'clients/change_password.html', {'form': form})