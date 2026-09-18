from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import (
    ConversationHandler,
)
from app.handlers.helper.menu import (_notes_menu)
from app.handlers.helper.format import (_fmt_note)
from app.core.calendar.services import CalendarService
from app.handlers.constants import (NoteState)


async def del_note_receive_id(update, context) -> int:
    text = (update.message.text or "").strip()
    try:
        note_id = int(text)
    except ValueError:
        await update.message.reply_text("Номер должен быть числом. Введите ещё раз:")
        return NoteState.DEL_NOTE_ID

    service: CalendarService = context.application.calendar_service
    note = await service.read_note(note_id, user_id=update.effective_user.id)

    if note is None:
        await update.message.reply_text(
            f"Заметка #{note_id} не найдена. Попробуйте другой номер:"
        )
        return NoteState.DEL_NOTE_ID

    await update.message.reply_text(
        f"Удалить заметку #{note_id}?\n\n{_fmt_note(note)}",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🗑 Да", callback_data=f"notes:delete:{note_id}"),
                InlineKeyboardButton("↩️ Нет", callback_data="notes:delete_cancel"),
            ]
        ]),
    )
    return ConversationHandler.END


async def delete_note_confirm(update, context) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data or ""

    if data == "notes:delete_cancel":
        # убираем клавиатуру, но НЕ трогаем текст (заметку)
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except BadRequest:
            pass
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Удаление отменено.",
            reply_markup=_notes_menu(),
        )
        return

    parts = data.split(":")
    if len(parts) != 3 or parts[0] != "notes" or parts[1] != "delete":
        return
    try:
        note_id = int(parts[2])
    except ValueError:
        return

    service: CalendarService = context.application.calendar_service
    deleted = await service.delete_note(note_id, user_id=update.effective_user.id)
    # убираем клавиатуру, но НЕ трогаем текст (заметку)
    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except BadRequest:
        pass
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"🗑 Заметка #{note_id} удалена." if deleted else f"⚠️ Заметка #{note_id} не найдена.",
        reply_markup=_notes_menu(),
    )


async def delete_note_confirm_all(update, context) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data or ""

    if data == "notes:delete_all_cancel":
        # убираем клавиатуру, но НЕ трогаем текст (заметку)
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except BadRequest:
            pass
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Удаление отменено.",
            reply_markup=_notes_menu(),
        )
        return

    parts = data.split(":")
    if len(parts) != 2 or parts[0] != "notes" or parts[1] != "delete_all_confirm":
        return

    service: CalendarService = context.application.calendar_service
    await service.delete_all_notes(user_id=update.effective_user.id)
    # убираем клавиатуру, но НЕ трогаем текст (заметку)
    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except BadRequest:
        pass
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"🗑 Все заметки удалены.",
        reply_markup=_notes_menu(),
    )
    return
