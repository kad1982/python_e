from dataclasses import dataclass

from telegram.ext import (
    BaseHandler,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from app.handlers.constants import (
    NoteState
)
from app.handlers.helper.export import export_handler

from app.handlers.helper.login import (
    login_start,
    login_last_name,
    login_first_name,
    login_middle_name, my_id,
)

from app.handlers.commands import (
    create_note_handler, display_note_handler, display_sorted_notes_handler,
    edit_note_request_id_handler, edit_note_menu_handler, read_note_request_id_handler,
    del_note_request_id_handler, del_all_note_request_handler, appointment_callback
)

from app.handlers.helper.menu import (_notes_menu, _sort_menu, notes_menu, _show_edit_menu, cancel_conversation)

from app.handlers.helper.format import (_fmt_note, _parse_date, _parse_time)
from app.handlers.helper.edit import (_start_editing, edit_note_receive_id, edit_note_name,
                                      edit_note_calendar, edit_note_time, edit_note_details)
from app.handlers.helper.delete import (delete_note_confirm, del_note_receive_id, delete_note_confirm_all)

from app.handlers.helper.create import (create_note_name, create_note_calendar,
                                        create_note_date, create_note_time, create_note_details)
from app.handlers.helper.read import read_note_receive_id

from app.handlers.helper.share import (
    share_request_id, share_receive_id, share_toggle,
)
from app.handlers.helper.shared import (
    shared_menu_request, shared_receive_id, shared_command, my_public_handler,
)


@dataclass
class Handler:
    handler: BaseHandler


HANDLERS: tuple[Handler, ...] = (
    Handler(
        handler=ConversationHandler(
            entry_points=[CommandHandler("login", login_start)],
            states={
                NoteState.LOGIN_LAST_NAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, login_last_name),
                ],
                NoteState.LOGIN_FIRST_NAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, login_first_name),
                ],
                NoteState.LOGIN_MIDDLE_NAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, login_middle_name),
                ],
            },
            fallbacks=[CommandHandler("cancel", cancel_conversation)],
        )),
    Handler(handler=CallbackQueryHandler(appointment_callback, pattern=r"^appt:(accept|decline):\d+$")),
    Handler(handler=CommandHandler("start", notes_menu)),

    # --- /share без аргумента и кнопка «Поделиться событием» ---
    Handler(
        handler=ConversationHandler(
            entry_points=[
                CommandHandler("share", share_request_id),  # если без args
                CallbackQueryHandler(share_request_id, pattern=r"^notes:share$"),
            ],
            states={
                NoteState.SHARE_NOTE_ID: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, share_receive_id),
                ],
            },
            fallbacks=[CommandHandler("cancel", cancel_conversation)],
        )
    ),

    # --- /shared без аргумента и кнопка «Общие события» ---
    Handler(
        handler=ConversationHandler(
            entry_points=[
                CallbackQueryHandler(shared_menu_request, pattern=r"^notes:shared$"),
            ],
            states={
                NoteState.VIEW_SHARED_ID: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, shared_receive_id),
                ],
            },
            fallbacks=[CommandHandler("cancel", cancel_conversation)],
        )
    ),

    # --- кнопка переключения публичности ---
    Handler(handler=CallbackQueryHandler(share_toggle, pattern=r"^share_toggle:\d+$")),

    Handler(
        handler=ConversationHandler(
            entry_points=[
                CommandHandler("create_note", create_note_handler),
                CallbackQueryHandler(create_note_handler, pattern=r"^notes:create$"),
            ],
            states={
                NoteState.NOTE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_note_name)],
                NoteState.NOTE_DATE: [CallbackQueryHandler(create_note_calendar)],
                NoteState.NOTE_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_note_time)],
                NoteState.NOTE_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_note_details)],
            },
            fallbacks=[CommandHandler("cancel", cancel_conversation)],
        )
    ),

    Handler(handler=CommandHandler("my_public", my_public_handler)),
    Handler(handler=CommandHandler("myId", my_id)),
    Handler(handler=CallbackQueryHandler(export_handler, pattern=r"^notes:export$")),
    Handler(handler=CommandHandler("export", export_handler)),

    Handler(
        handler=ConversationHandler(
            entry_points=[
                CallbackQueryHandler(read_note_request_id_handler, pattern=r"^notes:read$"),
            ],
            states={
                NoteState.READ_NOTE_ID: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, read_note_receive_id),
                ],
            },
            fallbacks=[CommandHandler("cancel", cancel_conversation)],
        )
    ),

    Handler(
        handler=ConversationHandler(
            entry_points=[
                CallbackQueryHandler(edit_note_request_id_handler, pattern=r"^notes:edit$"),
            ],
            states={
                NoteState.EDIT_NOTE_ID: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, edit_note_receive_id),
                ],
                NoteState.EDIT_NOTE_MENU: [
                    CallbackQueryHandler(edit_note_menu_handler, pattern=r"^edit_field:"),
                ],
                NoteState.EDIT_NOTE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_note_name)],
                NoteState.EDIT_NOTE_DATE: [CallbackQueryHandler(edit_note_calendar)],
                NoteState.EDIT_NOTE_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_note_time)],
                NoteState.EDIT_NOTE_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_note_details)],
            },
            fallbacks=[CommandHandler("cancel", cancel_conversation)],
        )
    ),

    Handler(
        handler=ConversationHandler(
            entry_points=[
                CallbackQueryHandler(del_note_request_id_handler, pattern=r"^notes:del$"),
            ],
            states={
                NoteState.DEL_NOTE_ID: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, del_note_receive_id),
                ],
            },
            fallbacks=[CommandHandler("cancel", cancel_conversation)],
        )
    ),

    Handler(handler=CallbackQueryHandler(delete_note_confirm, pattern=r"^notes:delete(:\d+|_cancel)$")),
    Handler(handler=CallbackQueryHandler(
        del_all_note_request_handler,  # показать подтверждение
        pattern=r"^notes:delete_all$",
    )),
    Handler(handler=CallbackQueryHandler(
        delete_note_confirm_all,  # удалить / отменить
        pattern=r"^notes:delete_all_(confirm|cancel)$",
    )),

    Handler(handler=CommandHandler("calendar", display_note_handler)),
    Handler(handler=CallbackQueryHandler(display_note_handler, pattern=r"^notes:list$")),

    Handler(handler=CommandHandler("notes_sort", display_sorted_notes_handler)),
    Handler(handler=CallbackQueryHandler(display_sorted_notes_handler, pattern=r"^notes_sort:\w+:(asc|desc)$")),
    Handler(handler=CallbackQueryHandler(display_sorted_notes_handler, pattern=r"^notes:sort$")),
)
