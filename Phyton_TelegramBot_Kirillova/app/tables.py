import asyncio

from app.core.users.models import User  # noqa: F401
from app.core.calendar.models import Calendar # noqa: F401
from app.infra.postgres.base import Base
from app.infra.postgres.db import Database
from settings.config import settings


async def main() -> None:
    db = Database(settings.POSTGRES_DSN, declarative_base=Base)
    try:
        await db.create_tables()
    finally:
        await db.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
    print("Tables created.")