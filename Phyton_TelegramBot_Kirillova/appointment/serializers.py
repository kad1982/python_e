from rest_framework import serializers

from appointment.models import Appointment, ParticipantResponse, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name"]


class AppointmentSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    event_name = serializers.CharField(source="event.name", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "event", "event_name",
            "organizer",
            "participants",
            "date", "time",
            "duration_minutes",
            "details",
            "status", "status_display",
        ]
        read_only_fields = ["id", "organizer", "participants"]


class ParticipantResponseSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ParticipantResponse
        fields = ["id", "appointment", "user", "choice", "responded_at"]
        read_only_fields = ["id", "user", "responded_at"]