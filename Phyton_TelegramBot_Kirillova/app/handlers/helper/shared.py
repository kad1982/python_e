from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from app.core.calendar.services import CalendarService
from app.handlers.constants import NoteState


def _fmt_shared(note) -> str:
    return (
        f"<b>#{note.id} — {note.name}</b>\n"
        f"📅 {note.date.isoformat()}  ⏰ {note.time.strftime('%H:%M')}\n"
        f"📄 {note.details or '—'}"
    )


async def shared_menu_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Пользователь нажал «Общие события» — спрашиваем ID владельца."""
    query = update.callback_query
    await query.answer()
    context.user_data.clear()

    await query.edit_message_text(
        "👥 <b>Общие события</b>\n\n"
        "Введите Telegram ID пользователя, чьи публичные события хотите посмотреть "
        "(или /cancel):\n\n"
        "💡 Свой ID можно узнать командой /myId.",
        parse_mode=ParseMode.HTML,
    )
    return NoteState.VIEW_SHARED_ID


async def shared_receive_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = (update.message.text or "").strip()
    if not text.isdigit():
        await update.message.reply_text("ID должен быть числом. Попробуйте ещё раз:")
        return NoteState.VIEW_SHARED_ID

    owner_id = int(text)
    service: CalendarService = context.application.calendar_service

    notes = await service.get_public_events_of_user(owner_id)

    if not notes:
        await update.message.reply_text(
            f"📭 У пользователя <code>{owner_id}</code> нет публичных событий.",
            parse_mode=ParseMode.HTML,
        )
        return ConversationHandler.END

    header = (
        f"👥 <b>Общие события пользователя</b> "
        f"<code>{owner_id}</code> — {len(notes)}:\n\n"
    )
    body = "\n\n".join(_fmt_shared(n) for n in notes)
    text_out = header + body

    MAX = 4000
    for i in range(0, len(text_out), MAX):
        await update.message.reply_text(
            text_out[i:i + MAX],
            parse_mode=ParseMode.HTML,
        )

    return ConversationHandler.END


async def shared_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """/shared <owner_id> — посмотреть чужие публичные события."""
    args = context.args or []
    if not args:
        await update.message.reply_text(
            "Введите Telegram ID пользователя, чьи публичные события хотите посмотреть:"
        )
        return NoteState.VIEW_SHARED_ID

    if not args[0].isdigit():
        await update.message.reply_text("Использование: /shared <telegram_id>")
        return ConversationHandler.END

    context.args = [args[0]]
    return await shared_receive_id(update, context)


async def my_public_handler(update, context):
    service: CalendarService = context.application.calendar_service
    notes = await service.get_my_public_events(update.effective_user.id)
    if not notes:
        await update.message.reply_text("У вас нет публичных событий.")
        return
    header = f"🌐 <b>Ваши публичные события</b> — {len(notes)}:\n\n"
    body = "\n\n".join(_fmt_shared(n) for n in notes)
    await update.message.reply_text(header + body, parse_mode=ParseMode.HTML)
