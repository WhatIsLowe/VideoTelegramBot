import logging

import aiogram.exceptions
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database_handlers.functions import get_user_by_chat_id
from bot import bot


async def create_inline_menu(buttons: list[list], buttons_callback: list[list] = "None",
                             optional: str = None) -> InlineKeyboardMarkup:
    """Создает инлайн-меню.

    Принимает список кнопок и колбэки этих кнопок, а также необязательный аргумент.
    Кнопки и колбэки должны быть в формате вложенных списков.
    К примеру, если передать такие данные:
        - buttons = [["button_1"], ["button_2"]]
        - buttons_callback = [["btn_1"], ["btn_2"]]
        - optional = "change"
    то в результате получатся кнопки с названиями "button_1" и "button_2", и будут иметь такие reply_callback: "change_btn_1", "change_btn_2"
    :param buttons: Вложенный список кнопок.
    :param buttons_callback: Вложенный список колбэков.
    :param optional: Параметр, отвечающий за добавление к колбэку приставки.
    :return: InlineKeyboardMarkup с полученным меню.
    """
    inline_keyboard = []
    if buttons:
        for row, callback_row in zip(buttons, buttons_callback):
            buttons_line = []
            for button, button_callback in zip(row, callback_row):
                if optional is not None:
                    # Объединяем optional и коллбэк кнопки
                    # Например: optional = "change", button_callback = "select_admin"
                    # Результат: "change_select_admin"
                    button_callback = optional + "_" + button_callback
                buttons_line.append(InlineKeyboardButton(text=button, callback_data=button_callback))
            inline_keyboard.append(buttons_line)
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


async def change_inline_menu(chat_id: int, message_id: int, text: str = None,
                             markup: InlineKeyboardMarkup = None) -> None:
    """Заменяет предыдущее инлайн-меню - новым.

    Требуется передать хотя бы один из параметров text и (или) markup
    :param chat_id: ID чата пользователя.
    :param message_id: ID сообщения для замены.
    :param text: Новый текст. По-умолчанию, None.
    :param markup: Новая инлайн-разметка. По-умолчанию, None.
    """
    try:
        if text or markup:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=markup)
    except aiogram.exceptions.TelegramBadRequest as e:
        if 'Bad Request: message to edit not found' in str(e) or 'message to edit' in str(e):
            try:
                await bot.delete_message(chat_id=chat_id, message_id=message_id)
            except Exception as e:
                logging.error(f"Невозможно удалить сообщение с id {message_id}")
            finally:
                await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)
        else:
            logging.error(f"Error in change_inline_menu: {e}")


async def main_menu(chat_id: int) -> (str, InlineKeyboardMarkup):
    """Создает главное меню пользователя

    Проверяет наличие пользователя по chat_id в базе данных и возвращает меню в соответствии с ролью.
    Если пользователя нет в базе данных - вызывается меню выбора роли.
    :param chat_id: ID чата пользователя.
    :return: InlineKeyboardMarkup c главным меню.
    """
    text = "Главное меню"
    user_data = await get_user_by_chat_id(chat_id=chat_id)
    if user_data:
        logging.error(user_data[-1])
        buttons = [
            ['Смотреть видео'],
            ['2 опция'],
            ['3 опция'],
            ['Сменить роль'],
        ]
        callbacks = [
            ['watch_video'],
            ['none'],
            ['none'],
            ['change_role'],
        ]
        if user_data[-1] == 'admin':
            # TODO: Получать данные админ-меню и возвращает
            buttons.append(['Админ меню'])
            callbacks.append(['admin_menu'])

        return text, await create_inline_menu(buttons, callbacks)
    else:
        return await choose_role_menu()


async def choose_role_menu(opt: str = None) -> (str, InlineKeyboardMarkup):
    """Возвращает меню выбора роли
    :return: разметка клавиатуры
    """
    text = "Меню выбора роли"
    buttons = [
        ["Пользователь", "Администратор"]
    ]
    buttons_callback = [
        ['select_user', 'select_admin']
    ]

    return text, await create_inline_menu(buttons, buttons_callback, optional=opt)


async def admin_menu() -> (str, InlineKeyboardMarkup):
    text = "Меню администратора"

    buttons = [
        ['Статистика пользователей'],
        ['Установить напоминание'],
        ['Главное меню'],
    ]

    callbacks = [
        ['admin_get_users'],
        ['admin_set_reminder'],
        ['main_menu'],
    ]

    return text, await create_inline_menu(buttons, callbacks)


async def categories_menu(categories: dict, page: int = 0) -> InlineKeyboardMarkup:
    PAGE_SIZE = 5
    text = 'Выберите категорию'
    keys = list(categories.keys())
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    buttons = [[categories[key]] for key in keys[start:end]]
    buttons_callback = [["select_category_" + str(key)] for key in keys[start:end]]
    if end < len(keys):
        buttons.append(["Далее"])
        buttons_callback.append(["next_page_" + str(page + 1)])
    if page > 0:
        buttons.append(["Назад"])
        buttons_callback.append(["prev_page_" + str(page - 1)])
    buttons.append(["Главное меню"])
    buttons_callback.append(["main_menu"])
    return await create_inline_menu(buttons, buttons_callback)


async def under_video_menu(videos: list, video_index: int = 0, category_id: int = 0) -> InlineKeyboardMarkup:
    has_prev = video_index > 0
    has_next = video_index < len(videos) - 1
    current_video = videos[video_index] if videos else None
    buttons = []
    buttons_callback = []
    buttons.append([current_video['name']] if current_video else [])
    buttons_callback.append(["ignore"])

    page_buttons = []
    page_callback = []
    if has_prev:
        page_buttons.append("⬅️Предыдущее видео WIP")
        page_callback.append(f"prev_video_{category_id}_{video_index}")
    if has_next:
        page_buttons.append("Следующее видео➡️ WIP")
        page_callback.append(f"next_video_{category_id}_{video_index}")
        logging.warning(f"next_video_{category_id}_{video_index}")

    if page_buttons:
        buttons.append(page_buttons)
        buttons_callback.append(page_callback)

    buttons.append(["Выбрать видео"])
    buttons_callback.append([f'choose_video_{category_id}'])
    logging.warning(f'choose_video_{category_id}')

    buttons.append(["Выбрать категорию"])
    buttons_callback.append(['watch_video'])
    buttons.append(["Главное меню"])
    buttons_callback.append(["main_menu"])
    return await create_inline_menu(buttons, buttons_callback)


async def choose_video_menu(category_id: int, videos: list, page_index: int = 0) -> InlineKeyboardMarkup:
    """Меню выбора видео из указанной категории.

    :param category_id: ID категории.
    :param videos: Список видео.
    :param page_index: Номер страницы.
    """
    # Максимальное кол-во видео на 1 странице
    max_videos_per_page = 2

    pages = [videos[i:i + max_videos_per_page] for i in range(0, len(videos), max_videos_per_page)]
    # TODO: CRITICAL!!! Решить проблему с колбэком кнопки с видео. Желательно использовать file_id (id файла телеграм), но судя по всему оно превышает допустимую длину в 64 байта.
    buttons = [[InlineKeyboardButton(text=video['name'], callback_data=f'select_video_{video['id']}')] for video in
               pages[page_index]]

    page_buttons = []

    if page_index > 0:
        page_buttons.append(InlineKeyboardButton(text="◀️Назад", callback_data=f'prev_video_page_{category_id}_{page_index}'))
    if page_index + 1 < len(pages):
        page_buttons.append(InlineKeyboardButton(text="Далее▶️", callback_data=f'next_video_page_{category_id}_{page_index}'))
    if page_buttons:
        buttons.append(page_buttons)
    buttons.append([InlineKeyboardButton(text="Главное меню", callback_data='main_menu')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
