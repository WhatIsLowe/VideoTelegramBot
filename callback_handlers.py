import aiogram
import asyncio
import logging

from bot import bot, dp, db_handler
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
    bot.send_message(callback.message.chat.id, text=text, reply_markup=keyboard)


# @dp.callback_query(lambda call: call.data == 'change_role')
# async def change_role(callback: aiogram.types.CallbackQuery) -> None:
#     markup = await role_buttons(opt='change')
#     await bot.send_message(chat_id=callback.message.chat.id, text="Выбери роль:", reply_markup=markup)

@dp.callback_query(lambda call: call.data == 'change_role')
async def change_role(callback: aiogram.types.CallbackQuery) -> None:
    text, keyboard = await choose_role_menu(opt='change')
    await bot.send_message(chat_id=callback.message.chat.id, text=text, reply_markup=keyboard)


@dp.callback_query(lambda call: call.data.startswith('change'))
async def change_role(callback: aiogram.types.CallbackQuery):
    # FIXME: ОШИБКА!!! ИСПРАВИТЬ!!! Переброс на главное меню происходит раньше изменения роли в БД =>
    #  меню формируется независимо от новой установленной роли
    if 'admin' in callback.data:
        role = 'admin'
    elif 'user' in callback.data:
        role = 'user'
    else:
        return
    await db_handler.change_user_role(chat_id=callback.message.chat.id, new_role=role)
    text, keyboard = await main_menu(chat_id=callback.message.chat.id)
    await bot.send_message(chat_id=callback.message.chat.id, text=f'Вы успешно сменили роль на {role}!\n{text}',
                           reply_markup=keyboard)


@dp.callback_query(lambda call: call.data.startswith('admin'))
async def admin_callback(call: aiogram.types.CallbackQuery):
    if call.data == 'admin_menu':
        text, keyboard = await admin_menu()
        await bot.send_message(chat_id=call.message.chat.id, text=text, reply_markup=keyboard)
    else:
        # TODO: Добавить больше функционала в админ-панель
        pass


@dp.callback_query(lambda call: call.data == 'main_menu')
async def main_menu_callback(call: aiogram.types.CallbackQuery):
    text, keyboard = await main_menu(call.message.chat.id)
    await bot.send_message(chat_id=call.message.chat.id, text=text, reply_markup=keyboard)

@dp.callback_query()
async def log_chat(callback):
    logging.info(callback)
