from datetime import time, date

import pytest


@pytest.mark.asyncio
async def test_register_visitor_creates_user(
    user_service, user_repository, test_user_id, cleanup_users,
):
    """Регистрация создаёт пользователя. Используем test_user_id, НЕ test_user."""
    created = await user_service.register_visitor(
        user_id=test_user_id,
        username="ivan",
        first_name="Иван",
        last_name="Иванов",
    )

    assert created is True
    cleanup_users.append(test_user_id)        # ← удалим после теста

    fetched = await user_repository.get_by_id(test_user_id)
    assert fetched is not None
    assert fetched.username == "ivan"

@pytest.mark.asyncio
async def test_register_visitor_does_not_duplicate(
    user_service, test_user_id, cleanup_users,
):
    first = await user_service.register_visitor(user_id=test_user_id)
    second = await user_service.register_visitor(user_id=test_user_id)
    cleanup_users.append(test_user_id)

    assert first is True
    assert second is False


@pytest.mark.asyncio
async def test_register_visitor_increments_user_count_only_once(
    user_service, stats_service_mock, test_user_id, cleanup_users,
):
    await user_service.register_visitor(user_id=test_user_id)
    await user_service.register_visitor(user_id=test_user_id)
    cleanup_users.append(test_user_id)

    stats_service_mock.register_new_user.assert_awaited_once()

@pytest.mark.asyncio
async def test_create_event_for_existing_user(
    calendar_service, calendar_repository, test_user,
):
    """test_user уже создан фикстурой — можно сразу писать заметки."""
    note_id = await calendar_service.create_note(
        user_id=test_user,
        name="Событие",
        date=date(2026, 9, 20),
        time=time(10, 0),
        details="",
    )
    note = await calendar_repository.read_note(note_id, user_id=test_user)
    assert note is not None