from datetime import date as date_type, time as time_type
from datetime import datetime
from app.core.calendar.models import Calendar
from telegram.error import BadRequest


def _fmt_note(note: Calendar) -> str:
    return (
        f"<b>#{note.id} — {note.name}</b>\n"
        f"📅 {note.date.isoformat()}  ⏰ {note.time.strftime('%H:%M')}\n"
        f"{note.details}"
    )


def _parse_date(text: str) -> date_type | None:
    try:
        return datetime.strptime(text.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def _parse_time(text: str) -> time_type | None:
    try:
        return datetime.strptime(text.strip(), "%H:%M").time()
    except ValueError:
        return None

async def _safe_edit(query, text: str, **kwargs) -> None:
    """edit_message_text, который не падает на 'Message is not modified'."""
    try:
        await query.edit_message_text(text, **kwargs)
    except BadRequest as e:
        if "not modified" not in str(e).lower():
            raise