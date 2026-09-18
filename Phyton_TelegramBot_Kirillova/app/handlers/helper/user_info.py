from telegram import Update


def tg_user_kwargs(update: Update) -> dict:
    u = update.effective_user
    return {
        "user_id": u.id,
        "username": u.username,
        "first_name": u.first_name,
        "last_name": u.last_name,
    }