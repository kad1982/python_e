from django.urls import path
from . import views

app_name = 'rental_request'

urlpatterns = [
    path('create/<int:listing_pk>/', views.RentalRequestCreateView.as_view(), name='create_request'),
    path('my/', views.MyRequestsListView.as_view(), name='my_requests'),
    path('incoming/', views.IncomingRequestsListView.as_view(), name='incoming_requests'),
    path('<int:pk>/', views.RentalRequestDetailView.as_view(), name='request_detail'),
    path('<int:pk>/update-status/', views.RentalRequestUpdateStatusView.as_view(), name='update_status'),
]
