from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    register, home_view, profile_view,
    my_profile, profile_edit, change_password, custom_logout
)

app_name = 'clients'

urlpatterns = [
    # Главная страница
    path('', home_view, name='home'),

    # Аутентификация
    path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='clients/login.html'), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(template_name='clients/logout.html'), name='logout'),
    path('logout/', custom_logout, name='logout'),

    # Личный кабинет
    path('profile/', profile_view, name='profile'),
    path('profile/my/', my_profile, name='my_profile'),
    path('profile/edit/', profile_edit, name='profile_edit'),
    path('profile/change-password/', change_password, name='change_password'),
]
