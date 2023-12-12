# === MESSAGE HANDLERS ===
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot import dp
from database_handlers.functions import *
from menu_manager import *


@dp.message(CommandStart())
async def start(message: Message):
    if await is_user_in_db(message.chat.id):
        text, keyboard = await main_menu(message.chat.id)
    else:
        text, keyboard = await choose_role_menu()
    await message.answer(text, reply_markup=keyboard)

