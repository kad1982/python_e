from dataclasses import dataclass
from datetime import date as date_type

from sqlalchemy import update
from sqlalchemy.dialects.postgresql import insert

from app.core.stats.models import BotStatistics
from app.infra.postgres.db import Database


@dataclass
class StatsRepository:
    database: Database

    async def _ensure_row(self, session, today: date_type) -> None:
        stmt = (
            insert(BotStatistics)
            .values(date=today, user_count=0, event_count=0,
                    edited_events=0, cancelled_events=0)
            .on_conflict_do_nothing(index_elements=["date"])
        )
        await session.execute(stmt)

    async def increment(self, field: str, today: date_type) -> None:
        allowed = {"user_count", "event_count", "edited_events", "cancelled_events"}
        if field not in allowed:
            raise ValueError(field)

        async with self.database.session() as session:
            await self._ensure_row(session, today)
            stmt = (
                update(BotStatistics)
                .where(BotStatistics.date == today)
                .values(**{field: BotStatistics.__table__.c[field] + 1})
            )
            await session.execute(stmt)
            await session.commit()