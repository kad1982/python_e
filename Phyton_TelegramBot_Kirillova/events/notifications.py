from datetime import datetime

from django.db import transaction
from django.utils import timezone

from appointment.models import Appointment, ParticipantResponse


def format_appointment_text(appointment: Appointment) -> str:
    return (
        f"📅 <b>{appointment.event.name}</b>\n"
        f"🕒 {appointment.date} {appointment.time.strftime('%H:%M')}\n"
        f"📄 {appointment.details or '—'}\n"
        f"👤 Организатор: <code>{appointment.organizer_id}</code>\n"
        f"Статус: <b>{appointment.get_status_display()}</b>"
    )


def build_confirmation_keyboard(appointment_id: int):
    """Возвращает inline-клавиатуру. Замените на свою (telegram.InlineKeyboardMarkup)."""
    return {
        "inline_keyboard": [[
            {"text": "✅ Подтвердить", "callback_data": f"appt:accept:{appointment_id}"},
            {"text": "❌ Отклонить",   "callback_data": f"appt:decline:{appointment_id}"},
        ]]
    }


async def notify_participants(bot, appointment: Appointment) -> None:
    """Отправляет всем участникам уведомление с кнопками подтверждения."""
    text = format_appointment_text(appointment)
    keyboard = build_confirmation_keyboard(appointment.id)

    for user in appointment.participants.all():
        try:
            await bot.send_message(
                chat_id=user.id,
                text=f"🔔 Вас пригласили на встречу:\n\n{text}",
                parse_mode="HTML",
                reply_markup=keyboard,
            )
        except Exception as e:
            # логируем, но не падаем — один недоступный пользователь не должен ломать рассылку
            print(f"Не удалось отправить уведомление {user.id}: {e}")


@transaction.atomic
def accept_appointment(appointment_id: int, user_id: int) -> Appointment:
    """Участник подтвердил встречу."""
    appt = Appointment.objects.select_for_update().get(pk=appointment_id)

    resp = ParticipantResponse.objects.get(appointment=appt, user_id=user_id)
    resp.choice = ParticipantResponse.Choice.ACCEPTED
    resp.responded_at = timezone.now()
    resp.save(update_fields=["choice", "responded_at"])

    appt.status = Appointment.Status.CONFIRMED
    appt.save(update_fields=["status"])
    return appt


@transaction.atomic
def decline_appointment(appointment_id: int, user_id: int) -> Appointment:
    """Участник отклонил встречу."""
    appt = Appointment.objects.select_for_update().get(pk=appointment_id)

    resp = ParticipantResponse.objects.get(appointment=appt, user_id=user_id)
    resp.choice = ParticipantResponse.Choice.DECLINED
    resp.responded_at = timezone.now()
    resp.save(update_fields=["choice", "responded_at"])

    # Если отклонил хотя бы один — встреча отменяется.
    # Если нужна логика «отменяется, только если отклонили ВСЕ» — поменяйте условие.
    appt.status = Appointment.Status.CANCELLED
    appt.save(update_fields=["status"])
    return appt