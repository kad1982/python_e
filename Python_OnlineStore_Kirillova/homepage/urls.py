from django.urls import path
# from django.views.decorators.cache import cache_page

from homepage import views

app_name = 'homepage'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('masters/', views.AboutView.as_view(), name='masters'),
    path('contacts/', views.AboutView.as_view(), name='contacts'),
    path('privacy/', views.AboutView.as_view(), name='privacy'),
    path('terms/', views.AboutView.as_view(), name='terms'),
    path('delivery/', views.AboutView.as_view(), name='delivery'),
]
