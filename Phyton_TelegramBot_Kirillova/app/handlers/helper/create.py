from telegram.constants import ParseMode
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from app.handlers.helper.format import (_parse_date, _parse_time, _safe_edit)
from app.handlers.helper.menu import (_notes_menu)

from telegram import (
    Update,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)
from app.core.calendar.services import CalendarService
from app.handlers.constants import (NoteState)


async def create_note_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = (update.message.text or "").strip()
    if not name:
        await update.message.reply_text("Название не может быть пустым. Введите ещё раз:")
        return NoteState.NOTE_NAME
    context.user_data["name"] = name  # type: ignore[index]

    # Создаем и отправляем календарь
    calendar, step = DetailedTelegramCalendar(locale="ru").build()
    await update.message.reply_text(
        f"Выберите {LSTEP[step]}:",
        reply_markup=calendar
    )
    return NoteState.NOTE_DATE


async def create_note_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    # Обрабатываем выбор даты
    result, key, step = DetailedTelegramCalendar(locale="ru").process(query.data)

    if not result and key:
        # Пользователь еще выбирает (год, месяц, день) — обновляем календарь
        await _safe_edit(
            query,
            f"Выберите {LSTEP[step]}:",
            reply_markup=key
        )
        return NoteState.NOTE_DATE

    elif result:

        # Дата выбрана! Сохраняем и переходим к выбору времени
        context.user_data["date"] = result  # type: ignore[index]
        # Показываем выбор времени (часы)
        await _safe_edit(
            query,
            f"Дата выбрана: <b>{result.isoformat()}</b>\n\n"
            f"Введите время в формате HH:MM (например, 15:30):",
            parse_mode=ParseMode.HTML,
        )
        return NoteState.NOTE_TIME

    return NoteState.NOTE_DATE


async def create_note_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    parsed = _parse_date(update.message.text or "")
    if parsed is None:
        await update.message.reply_text(
            "Неверный формат. Ожидается YYYY-MM-DD, например 2026-09-20:"
        )
        return NoteState.NOTE_DATE
    context.user_data["date"] = parsed  # type: ignore[index]
    await update.message.reply_text("Введите время в формате HH:MM:")
    return NoteState.NOTE_TIME


async def create_note_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = (update.message.text or "").strip()

    # Парсим "HH:MM"
    parsed = _parse_time(text)
    if parsed is None:
        await update.message.reply_text(
            "Неверный формат. Введите время в виде HH:MM, например 15:30:"
        )
        return NoteState.NOTE_TIME

    context.user_data["time"] = parsed  # type: ignore[index]
    await update.message.reply_text("Введите описание заметки:")
    return NoteState.NOTE_DETAILS


async def create_note_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    details = (update.message.text or "").strip()
    if not details:
        await update.message.reply_text("Описание не может быть пустым. Введите ещё раз:")
        return NoteState.NOTE_DETAILS

    service: CalendarService = context.application.calendar_service  # type: ignore[attr-defined]
    note_id = await service.create_note(
        user_id=update.effective_user.id,
        name=context.user_data["name"],  # type: ignore[index]
        date=context.user_data["date"],  # type: ignore[index]
        time=context.user_data["time"],  # type: ignore[index]
        details=details,
    )
    await update.message.reply_text(
        f"✅ Заметка создана. ID: {note_id}",
        reply_markup=_notes_menu(),
    )
    context.user_data.clear()  # type: ignore[union-attr]
    return ConversationHandler.END
