from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from app.core.users.services import UserService
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
)
from app.handlers.helper.format import (_fmt_note, _safe_edit)
from app.handlers.helper.menu import (_notes_menu, _sort_menu)
from app.core.calendar.services import CalendarService
from app.handlers.constants import (NoteState)
from telegram.error import BadRequest

from app.handlers.helper.user_info import tg_user_kwargs


async def appointment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data or ""
    parts = data.split(":")
    if len(parts) != 3 or parts[0] != "appt":
        return

    action, appt_id_str = parts[1], parts[2]
    try:
        appt_id = int(appt_id_str)
    except ValueError:
        return

    user_id = update.effective_user.id

    # Импорт функции Django-логики
    from events.notifications import accept_appointment, decline_appointment

    from asgiref.sync import sync_to_async

    if action == "accept":
        appt = await sync_to_async(accept_appointment)(appt_id, user_id)
        await query.edit_message_text(
            f"✅ Вы подтвердили встречу #{appt.id}.\nСтатус: {appt.get_status_display()}"
        )
    elif action == "decline":
        appt = await sync_to_async(decline_appointment)(appt_id, user_id)
        await query.edit_message_text(
            f"❌ Вы отклонили встречу #{appt.id}.\nСтатус: {appt.get_status_display()}"
        )


async def create_note_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    if query:
        await query.answer()
        await _safe_edit(
            query,
            "<strong><em>Вы выбрали пункт меню «Создание заметки»</em></strong>",
            parse_mode=ParseMode.HTML,
        )

    user_service: UserService = context.application.user_service  # type: ignore[attr-defined]
    await user_service.register_visitor(**tg_user_kwargs(update))

    if update.effective_chat and query and query.message:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Введите название заметки:",
        )
    context.user_data.clear()  # type: ignore[union-attr]
    return NoteState.NOTE_NAME


async def edit_note_menu_handler(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()
    data = query.data or ""
    parts = data.split(":")
    if len(parts) != 2 or parts[0] != "edit_field":
        return NoteState.EDIT_NOTE_MENU
    field = parts[1]

    if field == "cancel":
        context.user_data.clear()
        await _safe_edit(
            query,
            "❌ Редактирование отменено.",
            reply_markup=_notes_menu(),
        )
        return ConversationHandler.END

    if field == "save":
        service: CalendarService = context.application.calendar_service  # type: ignore[attr-defined]
        updated = await service.edit_note(
            note_id=context.user_data["note_id"],
            user_id=update.effective_user.id,
            name=context.user_data["name"],
            date=context.user_data["date"],
            time=context.user_data["time"],
            details=context.user_data["details"],
        )
        text_data = context.user_data  # type: ignore[union-attr]
        text = (
            f"\n<b>Номер заявки #{text_data['note_id']}</b>\n"
            f"📝 Название: <b>{text_data['name']}</b>\n"
            f"📅 Дата: {text_data['date'].isoformat()}\n"
            f"⏰ Время: {text_data['time'].strftime('%H:%M')}\n"
            f"📄 Описание: {text_data['details']}"
        )
        context.user_data.clear()
        await _safe_edit(
            query,
            "✅ Заметка обновлена." + text if updated else "⚠️ Не удалось обновить заметку.",
            parse_mode=ParseMode.HTML,
            reply_markup=_notes_menu(),
        )
        return ConversationHandler.END

    # --- поле "date" — показываем календарь ---
    if field == "date":
        calendar, step = DetailedTelegramCalendar(locale="ru").build()
        await _safe_edit(
            query,
            f"Выберите {LSTEP[step]}:",
            reply_markup=calendar,
        )
        return NoteState.EDIT_NOTE_DATE

    # --- остальные поля — текстом ---
    prompts = {
        "name": "Введите новое название:",
        "time": "Введите новое время  в виде HH:MM, например 15:30:",
        "details": "Введите новое описание:",
    }
    await _safe_edit(query, prompts.get(field, "Введите значение:"))
    return {
        "name": NoteState.EDIT_NOTE_NAME,
        "time": NoteState.EDIT_NOTE_TIME,
        "details": NoteState.EDIT_NOTE_DETAILS,
    }[field]


async def edit_note_request_id_handler(update, context) -> int:
    query = update.callback_query

    user_service: UserService = context.application.user_service
    await user_service.register_visitor(**tg_user_kwargs(update))

    service: CalendarService = context.application.calendar_service
    notes = await service.display_notes(user_id=update.effective_user.id)

    if not notes:
        if query:
            await query.answer()
            await _safe_edit(
                query,
                "📭 У вас пока нет заметок.",
                reply_markup=_notes_menu(),
            )
        return ConversationHandler.END

    if query:
        await query.answer()
        # убираем клавиатуру, но НЕ трогаем текст (заметку)
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except BadRequest:
            pass
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Вы выбрали «Редактировать заметку».\nВведите номер заметки:",
            parse_mode=ParseMode.HTML,
        )

    context.user_data.clear()
    return NoteState.EDIT_NOTE_ID


async def read_note_request_id_handler(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Точка входа: спрашиваем у пользователя ID заметки."""
    query = update.callback_query

    user_service: UserService = context.application.user_service
    await user_service.register_visitor(**tg_user_kwargs(update))

    service: CalendarService = context.application.calendar_service
    notes = await service.display_notes(user_id=update.effective_user.id)

    if not notes:
        if query:
            await query.answer()
            await _safe_edit(
                query,
                "📭 У вас пока нет заметок.",
                reply_markup=_notes_menu(),
            )
        return ConversationHandler.END
    if query:
        await query.answer()
        # убираем клавиатуру, но НЕ трогаем текст (заметку)
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except BadRequest:
            pass
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="<strong><em>Вы выбрали пункт меню «Просмотреть заметку»</em></strong>.\nВведите номер заметки, которую хотите просмотреть:",
            parse_mode=ParseMode.HTML,
        )
    context.user_data.clear()  # type: ignore[union-attr]
    return NoteState.READ_NOTE_ID


async def del_note_request_id_handler(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Точка входа: спрашиваем у пользователя ID заметки."""
    query = update.callback_query

    user_service: UserService = context.application.user_service
    await user_service.register_visitor(**tg_user_kwargs(update))

    service: CalendarService = context.application.calendar_service
    notes = await service.display_notes(user_id=update.effective_user.id)

    if not notes:
        if query:
            await query.answer()
            await query.edit_message_text(
                "📭 У вас пока нет заметок.",
                reply_markup=_notes_menu(),
            )
        return ConversationHandler.END
    if query:
        await query.answer()
        # убираем клавиатуру, но НЕ трогаем текст (заметку)
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except BadRequest:
            pass
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="<strong><em>Вы выбрали пункт меню «Удалить заметку»</em></strong>.\nВведите номер заметки, которую хотите удалить:",
            parse_mode=ParseMode.HTML,
        )
    context.user_data.clear()  # type: ignore[union-attr]
    return NoteState.DEL_NOTE_ID


async def del_all_note_request_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    user_service: UserService = context.application.user_service
    await user_service.register_visitor(**tg_user_kwargs(update))

    service: CalendarService = context.application.calendar_service
    notes = await service.display_notes(user_id=update.effective_user.id)

    if not notes:
        if query:
            await query.answer()
            await query.edit_message_text(
                "📭 У вас пока нет заметок.",
                reply_markup=_notes_menu(),
            )
        return ConversationHandler.END

    if query:
        await query.answer()
        await _safe_edit(
            query,
            "<strong><em>Вы выбрали пункт меню «Удалить все заметки»</em></strong>",
            parse_mode=ParseMode.HTML,
        )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Удалить все заметки?",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🗑 Да", callback_data="notes:delete_all_confirm"),
                InlineKeyboardButton("↩️ Нет", callback_data="notes:delete_all_cancel"),
            ]
        ]),
    )


async def display_note_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    user_service: UserService = context.application.user_service  # type: ignore[attr-defined]
    await user_service.register_visitor(**tg_user_kwargs(update))

    service: CalendarService = context.application.calendar_service  # type: ignore[attr-defined]
    notes = await service.display_notes(user_id=update.effective_user.id)

    if not notes:
        if query:
            await query.answer()
            await query.edit_message_text(
                "📭 У вас пока нет заметок.",
                reply_markup=_notes_menu(),
            )
        return ConversationHandler.END
    if query:
        await query.answer()
        await _safe_edit(
            query,
            "<strong><em>Вы выбрали пункт меню «Показать все заметки»</em></strong>",
            parse_mode=ParseMode.HTML,
        )

    text = "\n\n".join(_fmt_note(n) for n in notes)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=_notes_menu(),
    )


async def display_sorted_notes_handler(update, context) -> None:
    query = update.callback_query

    user_service: UserService = context.application.user_service
    await user_service.register_visitor(**tg_user_kwargs(update))

    service: CalendarService = context.application.calendar_service
    notes = await service.display_notes(user_id=update.effective_user.id)

    if not notes:
        if query:
            await query.answer()
            await query.edit_message_text(
                "📭 У вас пока нет заметок.",
                reply_markup=_notes_menu(),
            )
        return ConversationHandler.END

    if query:
        await query.answer()
        await _safe_edit(
            query,
            "<strong><em>Вы выбрали пункт меню «Сортировка заметок»</em></strong>",
            parse_mode=ParseMode.HTML,
        )

    if not query:
        # вызвали командой /notes_sort — просто показываем меню
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🔄 Выберите сортировку:",
            reply_markup=_sort_menu(),
        )
        return

    await query.answer()
    data = query.data or ""

    # случай 1: пользователь нажал «Сортировка заметок» — показываем меню
    if data == "notes:sort":
        await _safe_edit(
            query,
            "<strong><em>Вы выбрали пункт меню «Сортировка заметок»</em></strong>\n\n"
            "🔄 Выберите сортировку:",
            parse_mode=ParseMode.HTML,
            reply_markup=_sort_menu(),
        )
        return

    # случай 2: пользователь выбрал конкретную сортировку
    parts = data.split(":")
    if len(parts) != 3 or parts[0] != "notes_sort":
        return
    field = parts[1]
    reverse = parts[2] == "desc"

    notes = await service.display_sorted_notes(
        user_id=update.effective_user.id, sort_by=field, reverse=reverse
    )

    await _safe_edit(
        query,
        f"<strong><em>Вы выбрали сортировку по {field} ({'↓' if reverse else '↑'})</em></strong>",
        parse_mode=ParseMode.HTML,
    )
    text = "\n\n".join(_fmt_note(n) for n in notes)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=_notes_menu(),
    )


async def share_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """/share <id> — сделать событие публичным. Без аргумента — спросить номер."""
    args = context.args or []
    if not args:
        await update.message.reply_text(
            "Введите номер события, которое хотите сделать публичным:"
        )
        return NoteState.SHARE_NOTE_ID

    try:
        note_id = int(args[0])
    except ValueError:
        await update.message.reply_text("Использование: /share <номер события>")
        return ConversationHandler.END

    user_id = update.effective_user.id
    service: CalendarService = context.application.calendar_service

    note = await service.read_note(note_id, user_id=user_id)
    if note is None:
        await update.message.reply_text(f"Заметка #{note_id} не найдена.")
        return ConversationHandler.END

    ok = await service.make_public(note_id, user_id)
    await update.message.reply_text(
        f"✅ Событие #{note_id} теперь публичное." if ok
        else f"⚠️ Не удалось опубликовать #{note_id}.",
        reply_markup=_notes_menu(),
    )
    return ConversationHandler.END


async def unshare_command(update, context) -> None:
    args = context.args or []
    if not args or not args[0].isdigit():
        await update.message.reply_text("Использование: /unshare <номер события>")
        return
    note_id = int(args[0])
    service: CalendarService = context.application.calendar_service
    ok = await service.make_private(note_id, update.effective_user.id)
    await update.message.reply_text(
        f"🔒 Событие #{note_id} снова приватное." if ok
        else f"⚠️ Не удалось изменить #{note_id}."
    )




