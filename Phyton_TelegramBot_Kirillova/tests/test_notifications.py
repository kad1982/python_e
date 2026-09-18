from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.mark.asyncio
async def test_notify_participants_sends_to_each(monkeypatch):
    from events import notifications as notif

    # мок appointment с двумя участниками
    appointment = MagicMock()
    appointment.id = 42
    appointment.event.name = "Планёрка"
    from datetime import date, time
    appointment.date = date(2026, 9, 20)
    appointment.time = time(10, 0)
    appointment.details = ""
    appointment.organizer_id = 111
    appointment.get_status_display.return_value = "Ожидается"

    user1 = MagicMock(id=222)
    user2 = MagicMock(id=333)
    appointment.participants.all.return_value = [user1, user2]

    bot = MagicMock()
    bot.send_message = AsyncMock()

    await notif.notify_participants(bot, appointment)

    assert bot.send_message.await_count == 2
    # проверим, что отправлено правильным chat_id
    called_ids = [call.kwargs["chat_id"] for call in bot.send_message.await_args_list]
    assert 222 in called_ids
    assert 333 in called_ids