from bot import bot, dp, db_handler, db_video_handler
from database_handlers.functions import *
from menu_manager import *

# === CALLBACK HANDLERS ===

@dp.callback_query(lambda call: call.data == 'select_user' or call.data == 'select_admin')
async def set_user_role(callback: aiogram.types.CallbackQuery) -> None:
    if callback.data == 'select_user':
        role = 'user'
    else:
        role = 'admin'
    await write_user_in_db(callback, role)
    text, keyboard = await main_menu(callback.message.chat.id)
    # await bot.send_message(callback.message.chat.id, text=text, reply_markup=keyboard)
    await change_inline_menu(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=text,
                             markup=keyboard)


@dp.callback_query(lambda call: call.data == 'change_role')
async def change_role(callback: aiogram.types.CallbackQuery) -> None:
    text, keyboard = await choose_role_menu(opt='change')
    # await bot.send_message(chat_id=callback.message.chat.id, text=text, reply_markup=keyboard)
    await change_inline_menu(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=text,
                             markup=keyboard)


@dp.callback_query(lambda call: call.data.startswith('change'))
async def change_role(callback: aiogram.types.CallbackQuery):
    if 'admin' in callback.data:
        role = 'admin'
    elif 'user' in callback.data:
        role = 'user'
    else:
        return
    await db_handler.change_user_role(chat_id=callback.message.chat.id, new_role=role)
    text, keyboard = await main_menu(chat_id=callback.message.chat.id)
    # await bot.send_message(chat_id=callback.message.chat.id, text=f'Вы успешно сменили роль на {role}!\n{text}',
    #                        reply_markup=keyboard)
    # await change_inline_menu(callback.message.chat.id, callback.message.message_id, text="Жопа")
    await change_inline_menu(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=text,
                             markup=keyboard)


@dp.callback_query(lambda call: call.data.startswith('admin'))
async def admin_callback(callback: aiogram.types.CallbackQuery):
    # TODO: Добавить больше функционала в админ-панель
    if callback.data == 'admin_menu':
        text, keyboard = await admin_menu()
        # await bot.send_message(chat_id=call.message.chat.id, text=text, reply_markup=keyboard)
        await change_inline_menu(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=text,
                                 markup=keyboard)
    elif callback.data == 'admin_get_users':
        total_users, admin_users_count, admin_usernames, user_users_count = await get_users_count()
        text = f"""
            Общее кол-во пользователей: {total_users}
            Кол-во обычных пользователей: {user_users_count}
            Кол-во админов: {admin_users_count}
        """
        text_admins = "Админы:\n"
        for admin in admin_usernames:
            text_admins += '@' + admin + '\n'
        await bot.send_message(chat_id=callback.message.chat.id, text=text)
        await bot.send_message(chat_id=callback.message.chat.id, text=text_admins)
        pass


@dp.callback_query(lambda call: call.data == 'main_menu')
async def main_menu_callback(callback: aiogram.types.CallbackQuery):
    text, keyboard = await main_menu(callback.message.chat.id)
    # await bot.send_message(chat_id=call.message.chat.id, text=text, reply_markup=keyboard)
    await change_inline_menu(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=text,
                             markup=keyboard)


@dp.callback_query(lambda call: call.data == 'watch_video')
async def watch_video_callback(callback: aiogram.types.CallbackQuery):
    categories = await get_categories()
    keyboard = await categories_menu(categories)
    text = 'Выберите категорию:'
    await change_inline_menu(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=text,
                             markup=keyboard)


@dp.callback_query(lambda call: call.data.startswith('select_category'))
async def select_category_callback(callback: aiogram.types.CallbackQuery):
    category_id = int(callback.data.strip("_")[-1])
    videos = await get_videos(category_id)
    keyboard = await under_video_menu(False, False, videos, category_id=category_id)
    await bot.send_video(chat_id=callback.message.chat.id, video=videos[0]['file_id'], reply_markup=keyboard)


@dp.callback_query(lambda call: call.data.startswith('choose_video'))
async def choose_video_callback(callback: aiogram.types.CallbackQuery):
    """Обрабатывает нажатие кнопки "Выбрать видео"
    """
    category_id = int(callback.data.strip("_")[-1])
    videos = await get_videos(category_id)
    keyboard = await choose_video_menu(category_id, videos)
    await bot.edit

@dp.callback_query()
async def log_chat(callback):
    logging.info(callback)
