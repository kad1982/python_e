from datetime import datetime

from django.db import transaction

from appointment.models import Appointment, ParticipantResponse, User
from .services import is_user_free


class ParticipantBusy(Exception):
    """Участник занят в это время."""


@transaction.atomic
def invite_user_to_appointment(appointment: Appointment, user_id: int) -> ParticipantResponse:
    """Приглашает пользователя на встречу.

    1. Проверяет, свободен ли пользователь в дату/время встречи.
    2. Если занят — бросает ParticipantBusy.
    3. Если свободен — добавляет в участники, создаёт ParticipantResponse
       со статусом PENDING и переводит встречу в статус PENDING.
    """
    if appointment.status == Appointment.Status.CANCELLED:
        raise ValueError("Нельзя приглашать на отменённую встречу.")

    if appointment.participants.filter(id=user_id).exists():
        # уже приглашён — просто вернуть существующий ответ
        return ParticipantResponse.objects.get(appointment=appointment, user_id=user_id)

    if not is_user_free(
        user_id=user_id,
        date=appointment.date,
        time=appointment.time,
        duration_minutes=appointment.duration_minutes,
    ):
        raise ParticipantBusy(f"Пользователь {user_id} занят в это время.")

    user = User.objects.get(pk=user_id)
    appointment.participants.add(user)

    response, _ = ParticipantResponse.objects.get_or_create(
        appointment=appointment,
        user=user,
        defaults={"choice": ParticipantResponse.Choice.PENDING},
    )

    # Встреча переходит в статус «ожидается»
    if appointment.status != Appointment.Status.PENDING:
        appointment.status = Appointment.Status.PENDING
        appointment.save(update_fields=["status"])

    return response