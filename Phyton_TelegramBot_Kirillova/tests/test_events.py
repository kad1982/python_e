from datetime import date, time

import pytest


@pytest.mark.asyncio
async def test_create_event(calendar_service, calendar_repository, test_user):
    note_id = await calendar_service.create_note(
        user_id=test_user,
        name="Событие",
        date=date(2026, 9, 20),
        time=time(10, 0),
        details="",
    )

    note = await calendar_repository.read_note(note_id, user_id=test_user)
    assert note is not None
    assert note.name == "Событие"


@pytest.mark.asyncio
async def test_create_event_increments_event_count(
    calendar_service, stats_service_mock, test_user,
):
    await calendar_service.create_note(
        user_id=test_user,
        name="Событие",
        date=date(2026, 9, 20),
        time=time(10, 0),
        details="",
    )

    stats_service_mock.register_new_event.assert_awaited_once()