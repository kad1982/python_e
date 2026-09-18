from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from app.core.calendar.services import CalendarService
from app.handlers.constants import NoteState
from app.handlers.helper.format import _fmt_note
from app.handlers.helper.menu import _notes_menu


async def share_request_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Пользователь нажал «Поделиться событием» — просим номер."""
    query = update.callback_query
    await query.answer()
    context.user_data.clear()

    service: CalendarService = context.application.calendar_service
    notes = await service.display_notes(user_id=update.effective_user.id)

    if not notes:
        await query.edit_message_text(
            "📭 У вас нет событий, которыми можно поделиться.",
            reply_markup=_notes_menu(),
        )
        return ConversationHandler.END

    await query.edit_message_text(
        "🌐 <b>Поделиться событием</b>\n\n"
        "Введите номер события, которое хотите сделать публичным "
        "(или /cancel):",
        parse_mode=ParseMode.HTML,
    )
    return NoteState.SHARE_NOTE_ID


async def share_receive_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = (update.message.text or "").strip()
    if not text.isdigit():
        await update.message.reply_text("Номер должен быть числом. Попробуйте ещё раз:")
        return NoteState.SHARE_NOTE_ID

    note_id = int(text)
    user_id = update.effective_user.id
    service: CalendarService = context.application.calendar_service

    note = await service.read_note(note_id, user_id=user_id)
    if note is None:
        await update.message.reply_text(
            f"Заметка #{note_id} не найдена или не принадлежит вам. "
            "Попробуйте другой номер:"
        )
        return NoteState.SHARE_NOTE_ID

    current = note.is_public
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🔒 Сделать приватной" if current else "🌐 Сделать публичной",
                callback_data=f"share_toggle:{note_id}",
            )
        ],
        [InlineKeyboardButton("↩️ Готово", callback_data="notes:list")],
    ])

    await update.message.reply_text(
        f"Событие <b>#{note.id} — {note.name}</b>\n"
        f"Текущий статус: <b>{'публичное' if current else 'приватное'}</b>\n\n"
        "Изменить статус?",
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
    )
    return ConversationHandler.END


async def share_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Инлайн-кнопка переключения публичности."""
    query = update.callback_query
    await query.answer()

    data = query.data or ""
    parts = data.split(":")
    if len(parts) != 2 or parts[0] != "share_toggle":
        return

    try:
        note_id = int(parts[1])
    except ValueError:
        return

    user_id = update.effective_user.id
    service: CalendarService = context.application.calendar_service

    new_value = await service.toggle_public(note_id, user_id)
    if new_value is None:
        await query.edit_message_text("⚠️ Не удалось изменить статус.")
        return

    note = await service.read_note(note_id, user_id=user_id)
    status = "публичное" if new_value else "приватное"

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🔒 Сделать приватной" if new_value else "🌐 Сделать публичной",
                callback_data=f"share_toggle:{note_id}",
            )
        ],
        [InlineKeyboardButton("↩️ Готово", callback_data="notes:list")],
    ])

    await query.edit_message_text(
        f"Событие <b>#{note.id} — {note.name}</b>\n"
        f"Новый статус: <b>{status}</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
    )