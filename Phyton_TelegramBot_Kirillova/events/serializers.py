from rest_framework import serializers

from appointment.serializers import UserSerializer
from events.models import Events


class EventsSerializer(serializers.ModelSerializer):
    """Сериализатор события (таблица calendar)."""

    # user_id в вашей модели — это ForeignKey, отдаём только числовой id
    user_id = UserSerializer(read_only=True)

    class Meta:
        model = Events
        fields = ["id", "user_id", "name", "date", "time", "details"]
        read_only_fields = ["id", "user_id"]

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Название не может быть пустым.")
        return value.strip()

    def validate(self, attrs):
        return attrs