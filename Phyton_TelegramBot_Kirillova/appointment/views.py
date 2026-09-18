from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from appointment.models import Appointment, ParticipantResponse
from appointment.serializers import (
    AppointmentSerializer,
    ParticipantResponseSerializer,
)


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Appointment.objects
            .select_related("event", "organizer")
            .prefetch_related("participants")
            .order_by("-date", "-time")
        )


class ParticipantResponseViewSet(viewsets.ModelViewSet):
    serializer_class = ParticipantResponseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ParticipantResponse.objects.select_related("user", "appointment")