import asyncio
import json
import logging
import os

import aiogram.types
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database_handlers.postgresql_handler import PostgresqlHandler

import dotenv

dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

bot = Bot(os.getenv("TOKEN"))
dp = Dispatcher()
db_handler = PostgresqlHandler()


async def connect_to_db():
    await db_handler.set_table('users')
    await db_handler.open_connection(os.getenv('POSTGRES_CONNECTION_STRING'))
    await db_handler.create_table()


async def main():
    await connect_to_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    from database_handlers.functions import *
    from callback_handlers import *
    from menu_manager import *
    from message_handlers import *

    asyncio.run(main())
