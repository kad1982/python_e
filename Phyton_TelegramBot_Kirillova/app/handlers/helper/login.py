from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from app.core.users.services import UserService
from app.handlers.constants import NoteState


# ---------- Валидация ФИО ----------
def _valid_name(text: str) -> bool:
    """Русские/латинские буквы, дефис, пробел. Минимум 2 символа."""
    text = text.strip()
    if len(text) < 2 or len(text) > 50:
        return False
    return all(ch.isalpha() or ch in "- " for ch in text)


async def login_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Точка входа: спрашиваем фамилию."""
    context.user_data.clear()

    # чтобы у пользователя точно была запись в users
    user_service: UserService = context.application.user_service
    tg_user = update.effective_user
    await user_service.register_visitor(
        user_id=tg_user.id,
        username=tg_user.username,
        first_name=tg_user.first_name,
        last_name=tg_user.last_name,
    )

    await update.message.reply_text(
        "📝 <b>Вход в учётную запись</b>\n\n"
        "Введите вашу <b>фамилию</b>:",
        parse_mode=ParseMode.HTML,
    )
    return NoteState.LOGIN_LAST_NAME


async def login_last_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = (update.message.text or "").strip()
    if not _valid_name(text):
        await update.message.reply_text(
            "❌ Фамилия должна содержать только буквы, пробел или дефис "
            "(2–50 символов). Попробуйте ещё раз:"
        )
        return NoteState.LOGIN_LAST_NAME

    context.user_data["last_name"] = text
    await update.message.reply_text("Введите ваше <b>имя</b>:", parse_mode=ParseMode.HTML)
    return NoteState.LOGIN_FIRST_NAME


async def login_first_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = (update.message.text or "").strip()
    if not _valid_name(text):
        await update.message.reply_text(
            "❌ Имя должно содержать только буквы, пробел или дефис. Попробуйте ещё раз:"
        )
        return NoteState.LOGIN_FIRST_NAME

    context.user_data["first_name"] = text
    await update.message.reply_text(
        "Введите ваше <b>отчество</b> (или отправьте «-», если его нет):",
        parse_mode=ParseMode.HTML,
    )
    return NoteState.LOGIN_MIDDLE_NAME


async def login_middle_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = (update.message.text or "").strip()

    if text == "-":
        middle_name = ""
    else:
        if not _valid_name(text):
            await update.message.reply_text(
                "❌ Отчество должно содержать только буквы, пробел или дефис "
                "(или «-», если отчества нет). Попробуйте ещё раз:"
            )
            return NoteState.LOGIN_MIDDLE_NAME
        middle_name = text

    # Сохраняем ФИО в БД через UserService
    user_service: UserService = context.application.user_service
    tg_user = update.effective_user

    await user_service.update_full_name(
        user_id=tg_user.id,
        last_name=context.user_data["last_name"],
        first_name=context.user_data["first_name"],
        middle_name=middle_name,
    )

    full = " ".join(filter(None, [
        context.user_data["last_name"],
        context.user_data["first_name"],
        middle_name,
    ]))

    context.user_data.clear()

    await update.message.reply_text(
        "✅ <b>Вход выполнен</b>\n\n"
        f"Telegram ID: <code>{tg_user.id}</code>\n"
        f"ФИО: <b>{full}</b>\n\n"
        "Доступные команды:\n"
        "• /start\n"
        "• /calendar\n",
        parse_mode=ParseMode.HTML,
    )
    return ConversationHandler.END

# app/handlers/helper/login.py
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from app.core.users.services import UserService


async def my_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tg_user = update.effective_user
    text = (
        f"Telegram ID: <code>{tg_user.id}</code>"
    )

    await update.message.reply_text(text, parse_mode=ParseMode.HTML)