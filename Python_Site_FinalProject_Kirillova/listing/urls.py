from django.urls import path
from . import views

app_name = 'listing'

urlpatterns = [
    path('', views.ListingListView.as_view(), name='listing_list'),
    path('my_list/', views.MyListingListView.as_view(), name='my_listing_list'),
    path('<int:pk>/', views.ListingDetailView.as_view(), name='listing_detail'),
    path('create/', views.ListingCreateView.as_view(), name='listing_create'),
    path('<int:pk>/edit/', views.ListingUpdateView.as_view(), name='listing_update'),
    path('<int:pk>/delete/', views.ListingDeleteView.as_view(), name='listing_delete'),
]