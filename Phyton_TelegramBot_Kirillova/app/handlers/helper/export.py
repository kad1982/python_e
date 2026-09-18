import os
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes


DJANGO_BASE_URL = os.getenv("DJANGO_BASE_URL", "http://127.0.0.1:8000")
BOT_INTERNAL_SECRET = os.getenv("BOT_INTERNAL_SECRET", "change-me-to-a-long-random-string")


async def export_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Кнопка «📥 Выгрузить события» — присылает ссылку на скачивание CSV."""
    query = update.callback_query
    if query:
        await query.answer()

    telegram_id = update.effective_user.id

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{DJANGO_BASE_URL}/events/export-link/",
            params={"telegram_id": telegram_id, "format": "csv"},
            headers={"X-Bot-Secret": BOT_INTERNAL_SECRET},
        )

    if resp.status_code != 200:
        text = "⚠️ Не удалось подготовить файл. Попробуйте позже."
        if query:
            await query.edit_message_text(text)
        else:
            await update.message.reply_text(text)
        return

    url = resp.json()["url"]

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 Скачать CSV", url=url)],
    ])

    text = (
        "📥 <b>Выгрузка событий</b>\n\n"
        "Нажмите кнопку ниже, чтобы скачать файл.\n"
        "Ссылка действует 15 минут и содержит только <b>ваши</b> события."
    )

    if query:
        await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    else:
        await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)