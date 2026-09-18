import json
import os
from datetime import datetime

# Глобальные переменные
NOTES_FILE = "notes.json"
notes = []
next_id = 1


def load_notes():
    """Загружает заметки из JSON файла"""
    global notes, next_id

    if os.path.exists(NOTES_FILE):
        try:
            with open(NOTES_FILE, 'r', encoding='utf-8') as file:
                data = json.load(file)
                notes = data
                if notes:
                    next_id = max(note['id'] for note in notes) + 1
                else:
                    next_id = 1
        except (json.JSONDecodeError, FileNotFoundError):
            print("Ошибка загрузки файла. Будет создан новый файл.")
            notes = []
            next_id = 1
    else:
        notes = []
        next_id = 1


def save_notes():
    """Сохраняет заметки в JSON файл"""
    with open(NOTES_FILE, 'w', encoding='utf-8') as file:
        json.dump(notes, file, ensure_ascii=False, indent=2)


def create_note(title, content):
    """Создает новую заметку"""
    global next_id

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    note = {
        'id': next_id,
        'title': title,
        'content': content,
        'created_at': now,
        'updated_at': now
    }
    notes.append(note)
    next_id += 1
    save_notes()
    print(f"✅ Заметка создана! ID: {note['id']}")
    return note


def get_note_by_id(note_id):
    """Находит заметку по ID"""
    for note in notes:
        if note['id'] == note_id:
            return note
    return None


def read_note(note_id):
    """Читает заметку по ID"""
    note = get_note_by_id(note_id)
    if note:
        print("\n" + "-" * 50)
        print(f"ID: {note['id']}")
        print(f"Заголовок: {note['title']}")
        print(f"Содержание: {note['content']}")
        print(f"Создано: {note['created_at']}")
        print(f"Обновлено: {note['updated_at']}")
        print("-" * 50)
        return note
    else:
        print(f"❌ Заметка с ID {note_id} не найдена.")
        return None


def update_note(note_id, title=None, content=None):
    """Обновляет заметку по ID"""
    note = get_note_by_id(note_id)
    if note:
        if title:
            note['title'] = title
        if content:
            note['content'] = content
        note['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_notes()
        print(f"✅ Заметка ID {note_id} обновлена!")
        return True
    else:
        print(f"❌ Заметка с ID {note_id} не найдена.")
        return False


def delete_note(note_id):
    """Удаляет заметку по ID"""
    global notes

    note = get_note_by_id(note_id)
    if note:
        notes = [n for n in notes if n['id'] != note_id]
        save_notes()
        print(f"🗑️ Заметка ID {note_id} удалена!")
        return True
    else:
        print(f"❌ Заметка с ID {note_id} не найдена.")
        return False


def get_all_notes(sort_by="updated_at", reverse=True):
    """Возвращает все заметки с сортировкой"""
    if not notes:
        return []

    valid_sort_fields = {
        "id": lambda x: x['id'],
        "title": lambda x: x['title'].lower(),
        "created_at": lambda x: x['created_at'],
        "updated_at": lambda x: x['updated_at']
    }

    if sort_by in valid_sort_fields:
        return sorted(notes, key=valid_sort_fields[sort_by], reverse=reverse)
    else:
        print(f"⚠️ Неизвестное поле сортировки: {sort_by}. Используется сортировка по умолчанию.")
        return sorted(notes, key=valid_sort_fields["updated_at"], reverse=True)


def list_notes(sort_by="updated_at", reverse=True):
    """Выводит список всех заметок с сортировкой"""
    if not notes:
        print("📭 Нет заметок для отображения.")
        return

    sorted_notes = get_all_notes(sort_by, reverse)

    sort_names = {
        "id": "ID",
        "title": "заголовку",
        "created_at": "дате создания",
        "updated_at": "дате обновления"
    }

    direction = "по убыванию" if reverse else "по возрастанию"
    sort_name = sort_names.get(sort_by, sort_by)

    print(f"\n📋 Все заметки (сортировка по {sort_name}, {direction}):")
    print("=" * 70)
    for note in sorted_notes:
        print(f"ID: {note['id']:3} | {note['title']:30} | Обновлено: {note['updated_at']}")
    print("=" * 70)
    print(f"Всего заметок: {len(notes)}\n")


def clear_all_notes():
    """Удаляет все заметки"""
    global notes, next_id

    if notes:
        confirm = input("⚠️ Вы уверены, что хотите удалить все заметки? (да/нет): ")
        if confirm.lower() in ['да', 'yes', 'y', 'д']:
            notes = []
            next_id = 1
            save_notes()
            print("🗑️ Все заметки удалены!")
        else:
            print("❌ Операция отменена.")
    else:
        print("📭 Нет заметок для удаления.")


def print_menu():
    """Выводит главное меню"""
    print("\n" + "=" * 50)
    print("📝 ПРИЛОЖЕНИЕ ДЛЯ ЗАМЕТОК")
    print("=" * 50)
    print("1. 📝 Создать заметку")
    print("2. 📖 Прочитать заметку")
    print("3. ✏️ Редактировать заметку")
    print("4. 🗑️ Удалить заметку")
    print("5. 📋 Показать все заметки")
    print("6. 🔺Сортировка заметок")
    print("7. 📵 Удалить все заметки")
    print("0. ❌ Выйти")
    print("=" * 50)


def handle_sort_choice(choice):
    """Обрабатывает выбор сортировки"""
    sort_options = {
        '1': ("updated_at", True, "дате обновления (по убыванию)"),
        '2': ("updated_at", False, "дате обновления (по возрастанию)"),
        '3': ("created_at", True, "дате создания (по убыванию)"),
        '4': ("created_at", False, "дате создания (по возрастанию)"),
        '5': ("title", False, "заголовку (А-Я)"),
        '6': ("title", True, "заголовку (Я-А)"),
        '7': ("id", False, "ID (по возрастанию)"),
        '8': ("id", True, "ID (по убыванию)")
    }

    if choice in sort_options:
        sort_by, reverse, desc = sort_options[choice]
        print(f"\n🔄 Сортировка по {desc}")
        list_notes(sort_by, reverse)
    else:
        print("❌ Неверный выбор сортировки!")


def exists_app_note():
    return "👋 До свидания!"


def show_menu():
    confirm = input("⚠️ Открыть основное меню (да) или выйти из приложения (нет)?")
    if confirm.lower() in ['да', 'yes', 'y', 'д']:
        menu_change()
    else:
        print(exists_app_note())


def menu_change():
    print_menu()
    choice = input("Выберите действие (0-7): ").strip()

    if choice == '0':
        print(exists_app_note())

    elif choice == '1':
        flag_input = 0
        while not flag_input:
            title = input("Введите заголовок заметки: ").strip()
            if not title:
                print("❌ Заголовок не может быть пустым!")
            else:
                flag_input = 1
        flag_input = 0
        while not flag_input:
            content = input("Введите содержание заметки: ").strip()
            if not content:
                print("❌ Содержание не может быть пустым!")
            else:
                flag_input = 1
        create_note(title, content)
        show_menu()

    elif choice == '2':
        try:
            note_id = int(input("Введите ID заметки: "))
            read_note(note_id)
        except ValueError:
            print("❌ Введите корректный числовой ID!")
        show_menu()

    elif choice == '3':
        try:
            note_id = int(input("Введите ID заметки для редактирования: "))
            note = get_note_by_id(note_id)
            if note:
                print(f"Текущий заголовок: {note['title']}")
                title = input("Введите новый заголовок (оставьте пустым для сохранения текущего): ").strip()
                print(f"Текущее содержание: {note['content']}")
                content = input("Введите новое содержание (оставьте пустым для сохранения текущего): ").strip()
                update_note(note_id, title if title else None, content if content else None)
            else:
                print(f"❌ Заметка с ID {note_id} не найдена.")
        except ValueError:
            print("❌ Введите корректный числовой ID!")
        show_menu()

    elif choice == '4':
        try:
            note_id = int(input("Введите ID заметки для удаления: "))
            delete_note(note_id)
        except ValueError:
            print("❌ Введите корректный числовой ID!")
        show_menu()

    elif choice == '5':
        print("\n📋 ВСЕ ЗАМЕТКИ:")
        list_notes()
        show_menu()

    elif choice == '6':
        print("\n🔄 ВЫБОР СОРТИРОВКИ:")
        print("1. По дате обновления (по убыванию) - по умолчанию")
        print("2. По дате обновления (по возрастанию)")
        print("3. По дате создания (по убыванию)")
        print("4. По дате создания (по возрастанию)")
        print("5. По заголовку (А-Я)")
        print("6. По заголовку (Я-А)")
        print("7. По ID (по возрастанию)")
        print("8. По ID (по убыванию)")

        sort_choice = input("Выберите тип сортировки (1-8): ").strip()
        handle_sort_choice(sort_choice)
        show_menu()

    elif choice == '7':
        clear_all_notes()
        show_menu()

    else:
        print("❌ Неверный ввод! Пожалуйста, выберите действие от 0 до 7.")
        menu_change()
