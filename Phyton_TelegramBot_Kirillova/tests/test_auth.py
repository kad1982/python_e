from datetime import date, time

import pytest


@pytest.mark.asyncio
async def test_user_cannot_read_other_users_event(calendar_service, calendar_repository, test_user):
    """Пользователь A не должен видеть событие пользователя B."""
    note_id = await calendar_service.create_note(
        user_id=test_user, name="Чужое", date=date(2026, 9, 20),
        time=time(10, 0), details="",
    )

    note = await calendar_repository.read_note(note_id, user_id=222)
    assert note is None


@pytest.mark.asyncio
async def test_user_cannot_edit_other_users_event(calendar_service, test_user):
    note_id = await calendar_service.create_note(
        user_id=test_user, name="Чужое", date=date(2026, 9, 20),
        time=time(10, 0), details="",
    )

    updated = await calendar_service.edit_note(
        note_id=note_id, user_id=test_user+1, name="Взлом",
    )
    assert updated is False


@pytest.mark.asyncio
async def test_user_cannot_delete_other_users_event(calendar_service, test_user):
    note_id = await calendar_service.create_note(
        user_id=test_user, name="Чужое", date=date(2026, 9, 20),
        time=time(10, 0), details="",
    )

    deleted = await calendar_service.delete_note(note_id=note_id, user_id=test_user+1)
    assert deleted is False


@pytest.mark.asyncio
async def test_display_notes_returns_only_own(calendar_service, test_user):
    await calendar_service.create_note(
        user_id=test_user, name="A", date=date(2026, 9, 20), time=time(10, 0), details="",
    )

    notes = await calendar_service.display_notes(user_id=test_user)

    assert len(notes) == 1
    assert notes[0].name == "A"