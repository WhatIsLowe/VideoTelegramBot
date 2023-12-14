import logging

import aiogram.exceptions
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database_handlers.functions import is_user_in_db, get_user_by_chat_id
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
    try:
        if text or markup:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=markup)
    except aiogram.exceptions.TelegramBadRequest as e:
        if 'Bad Request: message to edit not found' in str(e):
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
            ['1 опция'],
            ['2 опция'],
            ['3 опция'],
            ['Сменить роль'],
        ]
        callbacks = [
            ['none'],
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
        # TODO: Вызов меню выбора роли пользователя (регистрация)

        pass


async def choose_role_menu(opt: str = None) -> (str, InlineKeyboardMarkup):
    """Возвращает меню выбора роли
    TODO: Переписать этот дебильный Docstring
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
        ['МЕНЮ 2'],
        ['Главное меню'],
    ]

    callbacks = [
        ['admin_get_users'],
        ['None'],
        ['main_menu'],
    ]

    return text, await create_inline_menu(buttons, callbacks)
