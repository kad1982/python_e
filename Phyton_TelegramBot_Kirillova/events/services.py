from dataclasses import dataclass
from datetime import date as date_type, datetime, time as time_type, timedelta

from django.db.models import Q

from appointment.models import Appointment, User


@dataclass(frozen=True)
class BusySlot:
    date: date_type
    start: time_type
    end: time_type
    title: str
    status: str

    def overlaps(self, other: "BusySlot") -> bool:
        if self.date != other.date:
            return False
        return self.start < other.end and other.start < self.end


def get_user_busy_slots(user_id: int) -> list[BusySlot]:
    """Все занятые интервалы пользователя.

    Учитывает встречи, где он организатор ИЛИ участник.
    Отменённые встречи игнорируются.
    """
    qs = (
        Appointment.objects
        .filter(
            Q(organizer_id=user_id) | Q(participants__id=user_id),
            status__in=[
                Appointment.Status.CONFIRMED,
                Appointment.Status.PENDING,
            ],
        )
        .select_related("event")
        .distinct()
        .order_by("date", "time")
    )

    slots: list[BusySlot] = []
    for appt in qs:
        end_dt = appt.end_datetime
        end_time = (
            end_dt.time() if end_dt.date() == appt.date else time_type(23, 59, 59)
        )
        slots.append(BusySlot(
            date=appt.date,
            start=appt.time,
            end=end_time,
            title=appt.event.name,
            status=appt.status,
        ))
    return slots


def is_user_free(user_id: int, date: date_type, time: time_type,
                 duration_minutes: int = 60) -> bool:
    """Свободен ли пользователь в указанный интервал."""
    from datetime import timedelta as _td

    start = datetime.combine(date, time)
    end = start + _td(minutes=duration_minutes)
    end_time = end.time() if end.date() == date else time_type(23, 59, 59)

    candidate = BusySlot(
        date=date, start=time, end=end_time, title="candidate", status="",
    )
    return all(not candidate.overlaps(s) for s in get_user_busy_slots(user_id))

@dataclass
class UserService:
    @staticmethod
    def register_telegram_user(
        telegram_id: int,
        username: str = "",
        first_name: str = "",
        last_name: str = "",
    ) -> tuple[User, bool]:
        """Создаёт или обновляет пользователя. Возвращает (user, created)."""
        user, created = User.objects.get_or_create(
            id=telegram_id,
            defaults={
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
            },
        )
        if not created:
            # обновим имена, если поменялись
            changed = (
                user.username != username
                or user.first_name != first_name
                or user.last_name != last_name
            )
            if changed:
                user.username = username
                user.first_name = first_name
                user.last_name = last_name
                user.save(update_fields=["username", "first_name", "last_name"])

        return user, created