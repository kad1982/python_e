from app.handlers.constants import (
    NoteState
)
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)
from app.handlers.helper.format import _safe_edit


async def cancel_conversation(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data.clear()
    if update.effective_chat:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Действие отменено.",
            reply_markup=_notes_menu(),
        )
    return ConversationHandler.END


def _notes_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Создать заметку", callback_data="notes:create")],
        [InlineKeyboardButton("📖 Прочитать заметку", callback_data="notes:read")],
        [InlineKeyboardButton("✏️ Редактировать заметку", callback_data="notes:edit")],
        [InlineKeyboardButton("🗑️ Удалить заметку", callback_data="notes:del")],
        [InlineKeyboardButton("📋 Показать все заметки", callback_data="notes:list")],
        [InlineKeyboardButton("🔄 Сортировка заметок", callback_data="notes:sort")],
        [InlineKeyboardButton("📵 Удалить все заметки", callback_data="notes:delete_all")],
        [InlineKeyboardButton("🌐 Поделиться событием", callback_data="notes:share")],
        [InlineKeyboardButton("👥 Общие события", callback_data="notes:shared")],
        [InlineKeyboardButton("👥 Мои опубликованные события", callback_data="notes:my_public")],
        [InlineKeyboardButton("📥 Выгрузить события", callback_data="notes:export")],

    ])


def _edit_fields_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📝 Название", callback_data="edit_field:name"),
            InlineKeyboardButton("📅 Дата", callback_data="edit_field:date"),
        ],
        [
            InlineKeyboardButton("⏰ Время", callback_data="edit_field:time"),
            InlineKeyboardButton("📄 Описание", callback_data="edit_field:details"),
        ],
        [
            InlineKeyboardButton("✅ Готово", callback_data="edit_field:save"),
            InlineKeyboardButton("❌ Отмена", callback_data="edit_field:cancel"),
        ],
    ])


async def _show_edit_menu(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Отправляет (или редактирует) сообщение с меню полей."""
    data = context.user_data  # type: ignore[union-attr]
    text = (
        f"<b>Редактирование заметки #{data['note_id']}</b>\n\n"
        f"📝 Название: <b>{data['name']}</b>\n"
        f"📅 Дата: {data['date'].isoformat()}\n"
        f"⏰ Время: {data['time'].strftime('%H:%M')}\n"
        f"📄 Описание: {data['details']}\n\n"
        f"Что редактируем?"
    )

    query = update.callback_query
    if query:
        await _safe_edit(
            query,
            text,
            reply_markup=_edit_fields_menu(),
            parse_mode=ParseMode.HTML,
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=_edit_fields_menu(),
            parse_mode=ParseMode.HTML,
        )
    return NoteState.EDIT_NOTE_MENU


async def notes_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat or not update.effective_user:
        return
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="📝 <b>Мои заметки</b>\nВыберите действие:",
        reply_markup=_notes_menu(),
        parse_mode=ParseMode.HTML,
    )


def _sort_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("По дате ↑", callback_data="notes_sort:date:asc"),
            InlineKeyboardButton("По дате ↓", callback_data="notes_sort:date:desc"),
        ],
        [
            InlineKeyboardButton("По времени ↑", callback_data="notes_sort:time:asc"),
            InlineKeyboardButton("По времени ↓", callback_data="notes_sort:time:desc"),
        ],
        [
            InlineKeyboardButton("По названию А-Я", callback_data="notes_sort:name:asc"),
            InlineKeyboardButton("По названию Я-А", callback_data="notes_sort:name:desc"),
        ],
        [
            InlineKeyboardButton("По ID ↑", callback_data="notes_sort:id:asc"),
            InlineKeyboardButton("По ID ↓", callback_data="notes_sort:id:desc"),
        ],
    ])
