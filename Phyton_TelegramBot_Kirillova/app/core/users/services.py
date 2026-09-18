from dataclasses import dataclass
from datetime import date

from app.core.users.repositories import UserRepository
from app.core.stats.services import StatsService


@dataclass
class UserService:
    repository: UserRepository
    stats_service: StatsService

    async def register_visitor(
        self,
        user_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> bool:
        created = await self.repository.create_user_if_not_exists(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        if created:
            await self.stats_service.register_new_user(date.today())
        return created

    async def update_full_name(
        self,
        user_id: int,
        last_name: str,
        first_name: str,
        middle_name: str = "",
    ) -> None:
        await self.repository.update_full_name(
            user_id=user_id,
            last_name=last_name,
            first_name=first_name,
            middle_name=middle_name,
        )