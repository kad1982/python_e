from app.handlers.helper.menu import (_notes_menu)

from app.handlers.helper.format import (_fmt_note)

from telegram import (
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)
from app.core.calendar.services import CalendarService
from app.handlers.constants import (
    NoteState
)


async def read_note_receive_id(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    text = (update.message.text or "").strip()
    try:
        note_id = int(text)
    except ValueError:
        await update.message.reply_text("Номер должен быть числом. Введите ещё раз:")
        return NoteState.READ_NOTE_ID

    service: CalendarService = context.application.calendar_service  # type: ignore[attr-defined]
    note = await service.read_note(note_id, user_id=update.effective_user.id)

    if note is None:
        await update.message.reply_text(
            f"Заметка #{note_id} не найдена. Попробуйте другой номер:"
        )
        return NoteState.READ_NOTE_ID

    await update.message.reply_text(
        _fmt_note(note),
        parse_mode=ParseMode.HTML,
        reply_markup=_notes_menu(),
    )
    return ConversationHandler.END
