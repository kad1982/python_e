from django.urls import path, include
from rest_framework.routers import DefaultRouter

from events.views import EventsViewSet, export_events, export_link

router = DefaultRouter()
router.register(r"events", EventsViewSet, basename="event")

urlpatterns = [
    # API
    path("api/", include(router.urls)),

    # существующие экспортные эндпоинты
    path("export/", export_events, name="export_events"),
    path("export-link/", export_link, name="export_link"),
]