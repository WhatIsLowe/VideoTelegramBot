import asyncio
import json
import logging
import os

import aiogram.types
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database_handler import SQLiteHandler, PostrgreSQLHandler

import dotenv

dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

bot = Bot(os.getenv("TOKEN"))
dp = Dispatcher()


# === Database ===
# db_handler = SQLiteHandler()
# db_handler.set_table('users')
# db_handler.open_connection()
db_handler = PostrgreSQLHandler()
async def connect_to_db():
    await db_handler.set_table('users')
    await db_handler.open_connection(os.getenv('POSTGRES_CONNECTION_STRING'))
    await db_handler.create_table()


async def create_inline_menu(buttons: list[list], buttons_callback: list[list] = "None"):
    inline_keyboard = []
    if buttons:
        for row, callback_row in zip(buttons, buttons_callback):
            buttons_line = []
            for button, button_callback in zip(row, callback_row):
                buttons_line.append(InlineKeyboardButton(text=button, callback_data=button_callback))
            inline_keyboard.append(buttons_line)
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


@dp.message(CommandStart())
async def start_message(message: types.Message):
    if await is_user_in_db(message.chat.id):
        await show_main_menu(message.chat.id)
    else:
        buttons = [
            ["Пользователь", "Администратор"]
        ]
        buttons_callback = [
            ['select_user', 'select_admin']
        ]
        keyboard = await create_inline_menu(buttons, buttons_callback)
        await message.answer(f"Привет! Я работаю!\nВыбери свою роль:", reply_markup=keyboard)


async def show_main_menu(chat_id):
    buttons = [
        ['1 опция'],
        ['2 опция'],
        ['3 опция'],
        ['Сменить роль'],
    ]
    keyboard = await create_inline_menu(buttons)
    await bot.send_message(chat_id=chat_id, text="Главное меню", reply_markup=keyboard)


async def is_user_in_db(chat_id) -> bool:
    user = await get_user_by_chat_id(chat_id)
    if user:
        return True
    else:
        return False


async def get_user_by_chat_id(chat_id: int) -> list | None:
    result = await db_handler.select_user(chat_id=chat_id)
    return result


async def write_user_in_db(callback: aiogram.types.CallbackQuery, role: str) -> None:
    chat_id = callback.message.chat.id
    username = callback.from_user.username
    firstname = callback.from_user.first_name
    await db_handler.write_user(chat_id=chat_id, username=username, firstname=firstname, role=role)


@dp.callback_query(lambda call: call.data == 'select_user' or call.data == 'select_admin')
async def set_user_role(callback: aiogram.types.CallbackQuery) -> None:
    if callback.data == 'select_user':
        role = 'user'
    else:
        role = 'admin'
    await write_user_in_db(callback, role)


@dp.callback_query()
async def log_chat(callback):
    logging.info(callback)


async def main():
    await connect_to_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
