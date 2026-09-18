from django.urls import path, include
from rest_framework.routers import DefaultRouter

from appointment.views import AppointmentViewSet, ParticipantResponseViewSet

router = DefaultRouter()
router.register(r"appointments", AppointmentViewSet, basename="appointment")
router.register(r"responses", ParticipantResponseViewSet, basename="response")

urlpatterns = [
    path("api/", include(router.urls)),
]