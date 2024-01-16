import json

from bot import bot, dp, db_handler
from database_handlers.functions import *
from menu_manager import *
from models import Form

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import datetime

# === CALLBACK HANDLERS ===

@dp.callback_query(lambda call: call.data == 'select_user' or call.data == 'select_admin')
async def set_user_role(callback: aiogram.types.CallbackQuery) -> None:
    if callback.data == 'select_user':
        role = 'user'
    else:
        role = 'admin'
    await write_user_in_db(callback, role)
    text, keyboard = await main_menu(callback.message.chat.id)
    await change_inline_menu(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=text,
                             markup=keyboard)


@dp.callback_query(lambda call: call.data == 'change_role')
async def change_role(callback: aiogram.types.CallbackQuery) -> None:
    text, keyboard = await choose_role_menu(opt='change')
    await change_inline_menu(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=text,
                             markup=keyboard)


@dp.callback_query(lambda call: call.data.startswith('change'))
async def change_role(callback: aiogram.types.CallbackQuery):
    """ Обработчик выбора роли.

    Позволяет установить/поменять роль пользователя.
    """
    if 'admin' in callback.data:
        role = 'admin'
    elif 'user' in callback.data:
        role = 'user'
    else:
        return
    await db_handler.change_user_role(chat_id=callback.message.chat.id, new_role=role)
    text, keyboard = await main_menu(chat_id=callback.message.chat.id)
    await change_inline_menu(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=text,
                             markup=keyboard)


@dp.callback_query(lambda call: call.data == 'main_menu')
async def main_menu_callback(callback: aiogram.types.CallbackQuery):
    """ Обработчик кнопки "Главное меню".

    После нажатия на кнопку текущее сообщение меняется на инлайн-главное-меню.
    """
    text, keyboard = await main_menu(callback.message.chat.id)
    # await bot.send_message(chat_id=call.message.chat.id, text=text, reply_markup=keyboard)
    await change_inline_menu(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=text,
                             markup=keyboard)


@dp.callback_query(lambda call: call.data == 'watch_video')
async def watch_video_callback(callback: aiogram.types.CallbackQuery):
    """ Обработчик кнопки "Смотреть видео".

    После нажатия на кнопку "Смотреть видео" текущее сообщение заменяется на новое, с текстом "Выберите категорию"
    и списком кнопок, каждая из которых - категория. Список категорий берется из базы, из таблицы "categories".
    """
    subjects = await get_subjects()
    keyboard = await categories_menu(subjects)
    text = 'Выберите категорию:'
    await change_inline_menu(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=text,
                             markup=keyboard)


@dp.callback_query(lambda call: call.data.startswith('select_category'))
async def select_category_callback(callback: aiogram.types.CallbackQuery):
    """ Обработчик выбора категорий.

    После выбора категории подгружается список видео, которые соответствуют этой категории
    и отправляется первое видео с прикрепленным инлайн-меню.
    """
    subject_id = int(callback.data.strip("_")[-1])
    videos = await get_videos_by_subject(subject_id=subject_id)
    # TODO: Реализовать механизм переключения видео
    keyboard = await under_video_menu(videos=videos, category_id=subject_id)
    # Удаляет меню с выбором категории
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    # Отправляет первое видео из категории с новым меню
    await bot.send_video(chat_id=callback.message.chat.id, video=videos[0]['file_id'], reply_markup=keyboard)


@dp.callback_query(lambda call: call.data.startswith('choose_video'))
async def choose_video_callback(callback: aiogram.types.CallbackQuery):
    """Обрабатывает нажатие кнопки "Выбрать видео"

    После нажатия на кнопку "Выбрать видео" текущее сообщение удаляется и отправляется новое,
    состоящее из матрицы кнопок, текстом которых является название видео и при нажатии на них
    текущее сообщение удаляется и отправляется новое, состоящее из выбранного видео и инлайн-меню
    """
    subject_id = int(callback.data.strip("_")[-1])
    videos = await get_videos_by_subject(subject_id=subject_id)
    keyboard = await choose_video_menu(subject_id, videos)
    # Удаляет предыдущее сообщение с видео
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    # Отправляет новое сообщение со списком видео
    try:
        await bot.send_message(chat_id=callback.message.chat.id, text="Выберете видео:", reply_markup=keyboard)
    except Exception as e:
        logging.error(e)


@dp.callback_query(lambda c: c.data and (c.data.startswith('next_video_page') or c.data.startswith('prev_video_page')))
async def change_video_page(call: aiogram.types.CallbackQuery):
    """ Обрабатывает кнопки Далее и Назад в выборе видео
    """
    call_parts = call.data.split('_')
    direction = call_parts[0]
    subject_id = int(call_parts[-2])
    page_index = int(call_parts[-1])
    videos = await get_videos_by_subject(subject_id=subject_id)
    if direction == 'next':
        page_index += 1
    elif direction == 'prev':
        page_index -= 1
    keyboard = await choose_video_menu(subject_id, videos, page_index)
    await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=keyboard)


@dp.callback_query(lambda c: c.data and c.data.startswith('select_video'))
async def select_video(callback: aiogram.types.CallbackQuery):
    video_id = int(callback.data.split('_')[-1])
    video = await get_video(video_id)
    keyboard = await under_video_menu([video], category_id=await get_subject_id_by_video_id(video_id))
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    # Отправляет первое видео из категории с новым меню
    logging.info(video)
    await bot.send_video(chat_id=callback.message.chat.id, video=video['file_id'], reply_markup=keyboard)


# === ADMIN MENU ===


reminder_callback_set = 'admin_set_reminder'
reminder_callback_confirm = 'admin_confirm_reminder'

# Обработчик кнопки "Установить напоминание"
@dp.callback_query(lambda c: c.data == "admin_set_reminder")
async def set_reminder_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Введите ник пользователя:')
    # await Form.user_input.set()
    await state.set_state(Form.user_input)

# Обработчик ввода пользователя
@dp.message(Form.user_input)
async def process_user_input(message: types.Message, state: FSMContext):
    user_nickname = message.text
    user = await get_user_by_username(username=user_nickname)
    logging.info(user)
    if user is None:
        await bot.send_message(message.from_user.id, 'Пользователь не найден, попробуйте еще раз.')
    else:
        await state.update_data(username=user['username'])
        await bot.send_message(message.from_user.id, 'Выберите дату в формате ДД-ММ-ГГГГ:')
        # await Form.date_input.set()
        await state.set_state(Form.date_input.state)

# Обработчик ввода даты
@dp.message(Form.date_input)
async def process_date_input(message: types.Message, state: FSMContext):
    date_str = message.text
    try:
        date = datetime.datetime.strptime(date_str, '%d-%m-%Y').date()
        if date < datetime.date.today():
            raise ValueError
        await state.update_data(date=date)
        await bot.send_message(message.from_user.id, 'Введите время в формате ЧЧ:ММ:')
        # await Form.time_input.set()
        await state.set_state(Form.time_input)
    except ValueError:
        await bot.send_message(message.from_user.id, 'Неверный формат даты или дата в прошлом, попробуйте еще раз.')

# Обработчик ввода времени
@dp.message(Form.time_input)
async def process_time_input(message: types.Message, state: FSMContext):
    time_str = message.text
    try:
        time = datetime.datetime.strptime(time_str, '%H:%M').time()
        await state.update_data(time=time)
        await bot.send_message(message.from_user.id, 'Введите текст напоминания:')
        # await Form.text_input.set()
        await state.set_state(Form.text_input)
    except ValueError:
        await bot.send_message(message.from_user.id, 'Неверный формат времени, попробуйте еще раз.')

# Обработчик ввода текста напоминания
@dp.message(Form.text_input)
async def process_text_input(message: types.Message, state: FSMContext):
    text = message.text
    await state.update_data(text=text)
    data = await state.get_data()
    accept_button = InlineKeyboardButton(text="Установить", callback_data=reminder_callback_confirm)
    markup = InlineKeyboardMarkup(inline_keyboard=[[accept_button]])
    await bot.send_message(message.from_user.id, f'Установить напоминание?\nПользователь: {data["username"]}\nДата: {data["date"]}\nВремя: {data["time"]}\nТекст сообщения: {data["text"]}', reply_markup=markup)
    # await Form.confirm_input.set()
    await state.set_state('*')

# Обработчик кнопки "Установить"
@dp.callback_query(lambda c: c.data == reminder_callback_confirm)
async def confirm_reminder_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    data = await state.get_data()
    date_time = datetime.datetime.combine(data['date'], data['time'])
    await add_reminder(user=data['username'], date_time=date_time, text=data['text'])
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data='admin_menu')]])
    await bot.send_message(callback_query.from_user.id, 'Напоминание установлено.', reply_markup=markup)
    await state.clear()

async def clear_state(state: FSMContext):
    await state.clear()

@dp.callback_query(lambda call: call.data.startswith('admin'))
async def admin_callback(callback: aiogram.types.CallbackQuery):
    # TODO: Добавить больше функционала в админ-панель
    if callback.data == 'admin_menu':
        """ Обработчик нажатия на кнопку "Админ панель".

        После нажатия на кнопку "Админ панель" отправляется сообщение с админ меню.
        """
        text, keyboard = await admin_menu()
        await change_inline_menu(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=text,
                                 markup=keyboard)
    elif callback.data == 'admin_get_users':
        """ Обработчик нажатия кнопки "Статистика пользователей".

        Выводит статистику по пользователям из БД.
        """
        total_users, admin_users_count, admin_usernames, user_users_count = await get_users_count()
        text = f"""
        Общее кол-во пользователей: {total_users}
        Кол-во обычных пользователей: {user_users_count}
        Кол-во админов: {admin_users_count}
        """
        text_admins = "Админы:\n"
        for admin in admin_usernames:
            text_admins += '@' + admin + '\n'
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
        await bot.send_message(chat_id=callback.message.chat.id, text=text)
        await bot.send_message(chat_id=callback.message.chat.id, text=text_admins)
        text, keyboard = await admin_menu()
        await bot.send_message(chat_id=callback.message.chat.id, text=text, reply_markup=keyboard)
# === DEBUG ===
@dp.callback_query()
async def log_chat(callback):
    logging.info(callback)
