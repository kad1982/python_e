import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.users.models import User
from app.core.calendar.models import Calendar
from app.core.users.repositories import UserRepository
from app.core.calendar.repositories import CalendarRepository
from app.core.users.services import UserService
from app.core.calendar.services import CalendarService
from settings.config import settings

# ----- КОНСТАНТА: id тестового пользователя -----
TEST_USER_ID = -900000001


# ----- ФИКСТУРА 1: только даёт id, БЕЗ вставки в БД -----
@pytest.fixture
def test_user_id():
    """Просто уникальный id для тестов. Никаких побочных эффектов в БД."""
    return TEST_USER_ID


# ----- ФИКСТУРА 2: создаёт пользователя и чистит после -----
@pytest_asyncio.fixture
async def test_user(db_session):
    """Создаёт пользователя в БД до теста и удаляет после.

    Используйте, когда тесту НУЖЕН уже существующий пользователь
    (например, чтобы создать заметку с FK на него).
    НЕ используйте в тестах, которые сами проверяют регистрацию.
    """
    async with db_session.session() as session:
        session.add(User(id=TEST_USER_ID))
        await session.commit()

    yield TEST_USER_ID

    async with db_session.session() as session:
        await session.execute(delete(Calendar).where(Calendar.user_id == TEST_USER_ID))
        await session.execute(delete(User).where(User.id == TEST_USER_ID))
        await session.commit()


# ----- ФИКСТУРА 3: чистит тестовых пользователей, созданных тестом -----
@pytest_asyncio.fixture
async def cleanup_users(db_session):
    """Собирает id пользователей, созданных тестом, и удаляет их после."""
    created: list[int] = []
    yield created

    if not created:
        return

    async with db_session.session() as session:
        await session.execute(delete(Calendar).where(Calendar.user_id.in_(created)))
        await session.execute(delete(User).where(User.id.in_(created)))
        await session.commit()


# ----- Общие фикстуры для БД и сервисов -----
@pytest_asyncio.fixture
async def db_session():
    dsn = settings.POSTGRES_DSN.get_secret_value()
    engine = create_async_engine(dsn)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    fake_db = MagicMock()
    fake_db.engine = engine
    fake_db.session = session_factory

    yield fake_db
    await engine.dispose()


@pytest.fixture
def user_repository(db_session):
    return UserRepository(database=db_session)


@pytest.fixture
def calendar_repository(db_session):
    return CalendarRepository(database=db_session)


@pytest.fixture
def stats_service_mock():
    from app.core.stats.services import StatsService
    svc = MagicMock(spec=StatsService)
    svc.register_new_user = AsyncMock()
    svc.register_new_event = AsyncMock()
    svc.register_edited_event = AsyncMock()
    svc.register_cancelled_event = AsyncMock()
    return svc


@pytest.fixture
def user_service(user_repository, stats_service_mock):
    return UserService(repository=user_repository, stats_service=stats_service_mock)


@pytest.fixture
def calendar_service(calendar_repository, stats_service_mock):
    return CalendarService(repository=calendar_repository, stats_service=stats_service_mock)
