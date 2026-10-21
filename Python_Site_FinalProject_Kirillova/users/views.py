from django.shortcuts import redirect
from django.contrib.auth import login
from django.contrib.auth.views import PasswordChangeView, LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, RedirectView, TemplateView

from .models import Users
from .forms import CustomUserCreationForm, UserProfileEditForm

# ==========================================
# 1. РЕГИСТРАЦИЯ
# ==========================================
class RegisterView(CreateView):
    model = Users
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:profile')

    def form_valid(self, form):
        # Сохраняем пользователя и сразу авторизуем его
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, 'Регистрация прошла успешно! Добро пожаловать.')
        return response


# ==========================================
# 2. ВХОД И ВЫХОД
# ==========================================
# Для входа лучше использовать встроенный класс Django.
# Он сам обработает форму и сделает редирект на LOGIN_REDIRECT_URL из settings.py
class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True

# Для выхода в Django 5+ используется LogoutView, но он принимает только POST.
# Если вы хотите свою логику с сообщениями, можно сделать так:
from django.contrib.auth.views import LogoutView

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('homepage:index')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, 'Вы успешно вышли из системы.')
        return super().dispatch(request, *args, **kwargs)


# ==========================================
# 3. ПРОСМОТР ПРОФИЛЯ
# ==========================================
class ProfileView(LoginRequiredMixin, DetailView):
    model = Users
    template_name = 'users/profile.html'
    context_object_name = 'user_obj'

    def get_object(self, queryset=None):
        # Возвращаем текущего авторизованного пользователя
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Здесь можно добавить статистику (количество аренд и т.д.)
        # context['my_rentals_count'] = self.request.user.rental_requests.count()
        return context


# ==========================================
# 4. РЕДАКТИРОВАНИЕ ПРОФИЛЯ
# ==========================================
class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = Users
    form_class = UserProfileEditForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        # Редактируем профиль текущего пользователя
        return self.request.user

    def form_valid(self, form):
        # Сохраняем форму, но не меняем пароль
        user = form.save(commit=False)
        # Пароль остается старым
        user.save()
        messages.success(self.request, 'Данные профиля успешно обновлены.')
        return super().form_valid(form)


# ==========================================
# 5. СМЕНА ПАРОЛЯ
# ==========================================
class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'users/change_password.html'
    success_url = reverse_lazy('users:profile')

    def form_valid(self, form):
        messages.success(self.request, 'Пароль успешно изменен!')
        return super().form_valid(form)