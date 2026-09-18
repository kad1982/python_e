from dataclasses import dataclass
from datetime import date as date_type, time as time_type
from typing import Literal

from sqlalchemy import and_, delete, select, update
from sqlalchemy.dialects.postgresql import insert

from app.core.calendar.models import Calendar
from app.infra.postgres.db import Database

SortField = Literal["id", "name", "date", "time"]


@dataclass
class CalendarRepository:
    database: Database

    async def create_note(
            self,
            user_id: int,
            name: str,
            date: date_type,
            time: time_type,
            details: str,
    ) -> int:
        async with self.database.session() as session:
            stmt = (
                insert(Calendar)
                .values(
                    user_id=user_id,
                    name=name,
                    date=date,
                    time=time,
                    details=details,
                )
                .returning(Calendar.id)
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.scalar_one()

    async def read_note(self, note_id: int, user_id: int) -> Calendar | None:
        async with self.database.session() as session:
            stmt = select(Calendar).where(
                and_(Calendar.id == note_id, Calendar.user_id == user_id)
            )
            return await session.scalar(stmt)

    async def edit_note(
            self,
            note_id: int,
            user_id: int,
            name: str | None = None,
            date: date_type | None = None,
            time: time_type | None = None,
            details: str | None = None,
    ) -> bool:
        values: dict = {}
        if name is not None:
            values["name"] = name
        if date is not None:
            values["date"] = date
        if time is not None:
            values["time"] = time
        if details is not None:
            values["details"] = details

        if not values:
            return False

        async with self.database.session() as session:
            stmt = (
                update(Calendar)
                .where(
                    and_(Calendar.id == note_id, Calendar.user_id == user_id)
                )
                .values(**values)
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0

    async def delete_note(self, note_id: int, user_id: int) -> bool:
        async with self.database.session() as session:
            stmt = delete(Calendar).where(
                and_(Calendar.id == note_id, Calendar.user_id == user_id)
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0

    async def delete_all_notes(self, user_id: int) -> bool:
        async with self.database.session() as session:
            stmt = delete(Calendar).where(Calendar.user_id == user_id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0

    async def display_notes(self, user_id: int) -> list[Calendar]:
        async with self.database.session() as session:
            stmt = select(Calendar).where(Calendar.user_id == user_id)
            result = await session.scalars(stmt)
            return list(result)

    async def display_sorted_notes(
            self,
            user_id: int,
            sort_by: SortField = "date",
            reverse: bool = False,
    ) -> list[Calendar]:
        column_map = {
            "id": Calendar.id,
            "name": Calendar.name,
            "date": Calendar.date,
            "time": Calendar.time,
        }
        column = column_map.get(sort_by, Calendar.date)

        async with self.database.session() as session:
            stmt = (
                select(Calendar)
                .where(Calendar.user_id == user_id)
                .order_by(column.desc() if reverse else column.asc())
            )
            result = await session.scalars(stmt)
            return list(result)

    async def set_public(self, note_id: int, user_id: int, is_public: bool) -> bool:
        """Меняет флаг публичности. Только владелец может менять."""
        async with self.database.session() as session:
            stmt = (
                update(Calendar)
                .where(and_(Calendar.id == note_id, Calendar.user_id == user_id))
                .values(is_public=is_public)
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0

    async def get_public_events_of_user(self, owner_id: int) -> list[Calendar]:
        """Все публичные события указанного пользователя."""
        async with self.database.session() as session:
            stmt = (
                select(Calendar)
                .where(and_(Calendar.user_id == owner_id, Calendar.is_public.is_(True)))
                .order_by(Calendar.date.asc(), Calendar.time.asc())
            )
            result = await session.scalars(stmt)
            return list(result)

    async def get_my_public_events(self, user_id: int) -> list[Calendar]:
        """Свои события с флагом is_public=True (для управления)."""
        async with self.database.session() as session:
            stmt = (
                select(Calendar)
                .where(and_(Calendar.user_id == user_id, Calendar.is_public.is_(True)))
                .order_by(Calendar.date.asc(), Calendar.time.asc())
            )
            result = await session.scalars(stmt)
            return list(result)