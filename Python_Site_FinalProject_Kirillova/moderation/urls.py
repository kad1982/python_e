from django.urls import path
from . import views

app_name = 'moderation'

urlpatterns = [
    path('', views.PendingListingsView.as_view(), name='pending_list'),
    path('<int:pk>/approve/', views.ApproveListingView.as_view(), name='approve'),
    path('<int:pk>/reject/', views.RejectListingView.as_view(), name='reject'),
]