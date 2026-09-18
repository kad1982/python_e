from dataclasses import dataclass

from sqlalchemy import update
from sqlalchemy.dialects.postgresql import insert

from app.core.users.models import User
from app.infra.postgres.db import Database


@dataclass
class UserRepository:
    database: Database

    async def get_by_id(self, user_id: int) -> User | None:
        """Возвращает пользователя по id или None."""
        async with self.database.session() as session:
            return await session.get(User, user_id)

    async def create_user_if_not_exists(
        self,
        user_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> bool:
        async with self.database.session() as session:
            stmt = (
                insert(User)
                .values(
                    id=user_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                )
                .on_conflict_do_nothing(index_elements=["id"])
                .returning(User.id)
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.scalar_one_or_none() is not None

    async def update_full_name(
        self,
        user_id: int,
        last_name: str,
        first_name: str,
        middle_name: str = "",
    ) -> None:
        async with self.database.session() as session:
            stmt = (
                update(User)
                .where(User.id == user_id)
                .values(
                    last_name=last_name,
                    first_name=first_name,
                    middle_name=middle_name,
                )
            )
            await session.execute(stmt)
            await session.commit()