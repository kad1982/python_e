from dataclasses import dataclass
from datetime import date as date_type

from app.core.stats.repositories import StatsRepository


@dataclass
class StatsService:
    repository: StatsRepository

    async def register_new_user(self, today: date_type) -> None:
        await self.repository.increment("user_count", today)

    async def register_new_event(self, today: date_type) -> None:
        await self.repository.increment("event_count", today)

    async def register_edited_event(self, today: date_type) -> None:
        await self.repository.increment("edited_events", today)

    async def register_cancelled_event(self, today: date_type) -> None:
        await self.repository.increment("cancelled_events", today)