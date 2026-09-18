from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from app.handlers.helper.menu import (_show_edit_menu)
from app.handlers.helper.format import (_parse_time, _safe_edit)
from telegram import (
    Update,
)
from telegram.ext import (
    ContextTypes,
)
from app.core.calendar.services import CalendarService
from app.handlers.constants import (NoteState)



async def edit_note_receive_id(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Состояние EDIT_NOTE_ID: получаем id от пользователя."""
    text = (update.message.text or "").strip()
    try:
        note_id = int(text)
    except ValueError:
        await update.message.reply_text(
            "Номер должен быть числом. Введите ещё раз:"
        )
        return NoteState.EDIT_NOTE_ID

    return await _start_editing(update, context, note_id)


async def _start_editing(
        update: Update, context: ContextTypes.DEFAULT_TYPE, note_id: int
) -> int:
    service: CalendarService = context.application.calendar_service  # type: ignore[attr-defined]
    note = await service.read_note(note_id, user_id=update.effective_user.id)
    if note is None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Заметка #{note_id} не найдена. Попробуйте другой номер:",
        )
        return NoteState.EDIT_NOTE_ID

    context.user_data["note_id"] = note_id  # type: ignore[index]
    context.user_data["name"] = note.name  # type: ignore[index]
    context.user_data["date"] = note.date  # type: ignore[index]
    context.user_data["time"] = note.time  # type: ignore[index]
    context.user_data["details"] = note.details  # type: ignore[index]

    return await _show_edit_menu(update, context)


async def edit_note_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = (update.message.text or "").strip()
    if not text:
        await update.message.reply_text("Название не может быть пустым. Введите ещё раз:")
        return NoteState.EDIT_NOTE_NAME
    context.user_data["name"] = text  # type: ignore[index]
    return await _show_edit_menu(update, context)


async def edit_note_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    result, key, step = DetailedTelegramCalendar(locale="ru").process(query.data)

    if not result and key:
        # Пользователь ещё листает календарь
        await _safe_edit(
            query,
            f"Выберите {LSTEP[step]}:",
            reply_markup=key,
        )
        return NoteState.EDIT_NOTE_DATE

    if result:
        # Дата выбрана — сохраняем и возвращаемся в меню полей
        context.user_data["date"] = result  # type: ignore[index]
        return await _show_edit_menu(update, context)

    return NoteState.EDIT_NOTE_DATE


async def edit_note_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    parsed = _parse_time(update.message.text or "")
    if parsed is None:
        await update.message.reply_text("Неверный формат. Введите время в виде HH:MM, например 15:30:")
        return NoteState.EDIT_NOTE_TIME
    context.user_data["time"] = parsed  # type: ignore[index]
    return await _show_edit_menu(update, context)


async def edit_note_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = (update.message.text or "").strip()
    if not text:
        await update.message.reply_text("Описание не может быть пустым. Введите ещё раз:")
        return NoteState.EDIT_NOTE_DETAILS
    context.user_data["details"] = text  # type: ignore[index]
    return await _show_edit_menu(update, context)
