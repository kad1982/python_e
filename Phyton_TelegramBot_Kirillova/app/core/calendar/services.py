from dataclasses import dataclass
from datetime import date as date_type, time as time_type

from app.core.calendar.models import Calendar
from app.core.calendar.repositories import CalendarRepository, SortField
from app.core.stats.services import StatsService


@dataclass
class CalendarService:
    repository: CalendarRepository
    stats_service: StatsService

    async def create_note(
        self,
        user_id: int,
        name: str,
        date: date_type,
        time: time_type,
        details: str,
    ) -> int:
        note_id = await self.repository.create_note(user_id, name, date, time, details)
        await self.stats_service.register_new_event(date.today())
        return note_id

    async def read_note(self, note_id: int, user_id: int) -> Calendar | None:
        return await self.repository.read_note(note_id, user_id)

    async def edit_note(
        self,
        note_id: int,
        user_id: int,
        name: str | None = None,
        date: date_type | None = None,
        time: time_type | None = None,
        details: str | None = None,
    ) -> bool:
        result = await self.repository.edit_note(
            note_id, user_id, name=name, date=date, time=time, details=details
        )
        if result:
            await self.stats_service.register_edited_event(date_type.today())
        return result

    async def delete_note(self, note_id: int, user_id: int) -> bool:
        result = await self.repository.delete_note(note_id, user_id)
        if result:
            await self.stats_service.register_cancelled_event(date_type.today())
        return result

    async def delete_all_notes(self, user_id: int) -> bool:
        result = await self.repository.delete_all_notes(user_id)
        if result:
            await self.stats_service.register_cancelled_event(date_type.today())
        return result

    async def display_notes(self, user_id: int) -> list[Calendar]:
        return await self.repository.display_notes(user_id)

    async def display_sorted_notes(
        self,
        user_id: int,
        sort_by: SortField = "date",
        reverse: bool = False,
    ) -> list[Calendar]:
        return await self.repository.display_sorted_notes(
            user_id, sort_by=sort_by, reverse=reverse
        )

    async def make_public(self, note_id: int, user_id: int) -> bool:
        return await self.repository.set_public(note_id, user_id, True)

    async def make_private(self, note_id: int, user_id: int) -> bool:
        return await self.repository.set_public(note_id, user_id, False)

    async def toggle_public(self, note_id: int, user_id: int) -> bool | None:
        """Переключает флаг. Возвращает новое значение или None, если не найдено."""
        note = await self.repository.read_note(note_id, user_id)
        if note is None:
            return None
        new_value = not note.is_public
        ok = await self.repository.set_public(note_id, user_id, new_value)
        return new_value if ok else None

    async def get_public_events_of_user(self, owner_id: int) -> list[Calendar]:
        return await self.repository.get_public_events_of_user(owner_id)

    async def get_my_public_events(self, user_id: int) -> list[Calendar]:
        return await self.repository.get_my_public_events(user_id)