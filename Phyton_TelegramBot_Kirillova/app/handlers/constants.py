from enum import IntEnum


class NoteState(IntEnum):
    # создание
    NOTE_NAME = 1
    NOTE_DATE = 2
    NOTE_TIME = 3
    NOTE_DETAILS = 4

    # редактирование
    EDIT_NOTE_ID = 10
    EDIT_NOTE_MENU = 11
    EDIT_NOTE_NAME = 12
    EDIT_NOTE_DATE = 13
    EDIT_NOTE_TIME = 14
    EDIT_NOTE_DETAILS = 15

    # чтение
    READ_NOTE_ID = 20

    # удаление
    DEL_NOTE_ID = 30

    # логин: ввод ФИО
    LOGIN_LAST_NAME = 40
    LOGIN_FIRST_NAME = 41
    LOGIN_MIDDLE_NAME = 42

    # Публичные события
    SHARE_NOTE_ID = 50  # пользователь вводит номер события для публикации
    VIEW_SHARED_ID = 51  # пользователь вводит ID владельца для просмотра
