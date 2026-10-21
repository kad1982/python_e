from django.urls import path

from homepage import views

app_name = 'homepage'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contacts/', views.AboutView.as_view(), name='contacts'),
    path('how_it_works/', views.HowItWorksView.as_view(), name='how_it_works'),
    path('delivery/', views.DeliveryView.as_view(), name='delivery'),
    path('sizes/', views.SizesView.as_view(), name='sizes'),
    path('terms/', views.TermsView.as_view(), name='terms'),
    path('faq/', views.FaqView.as_view(), name='faq'),
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
    path('agreement/', views.UserAgreementView.as_view(), name='user_agreement'),
]
