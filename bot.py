import asyncio
import logging
import os

import dotenv
from aiogram import Bot, Dispatcher

from database_handlers.postgresql_handler import ParentPostgresqlHandler, PostgresqlHandler, PostgresqlVideoHandler

dotenv.load_dotenv()

# Устанавливаем формат лога
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


bot = Bot(os.getenv("TOKEN"))
dp = Dispatcher()
db_handler = PostgresqlHandler()
db_video_handler = PostgresqlVideoHandler()


async def connect_to_db():
    # Устанавливаем название таблицы с данными пользователей
    await db_handler.set_table('users')

    # Устанавливаем название таблицы с данными для видео
    await db_video_handler.set_video_table('videos')
    # Для категорий видео
    await db_video_handler.set_categories_table('categories')

    # Подключаемся к БД Postgres
    await ParentPostgresqlHandler.open_connection(os.getenv('POSTGRES_CONNECTION_STRING'))

    # Создаем таблицы users, videos, categories если их нет
    await db_handler.create_table_if_not_exist()
    await db_video_handler.create_table_if_not_exist()


async def main():
    # Запускаем функцию подключения к БД
    await connect_to_db()
    # Запускаем бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Выполняем импорт необходимых модулей
    from database_handlers.functions import *
    from callback_handlers import *
    from menu_manager import *
    from message_handlers import *

    # Запускаем функцию main
    asyncio.run(main())
