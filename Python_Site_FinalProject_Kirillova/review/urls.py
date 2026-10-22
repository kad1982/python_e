from django.urls import path
from . import views

app_name = 'review'

urlpatterns = [
    path('add/<int:request_pk>/', views.AddReviewView.as_view(), name='add_review'),
]