import asyncio
import logging
import os

import dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from database_handlers.postgresql_handler import ParentPostgresqlHandler, PostgresqlHandler, PostgresqlVideoHandler, PostgresqlRemindersHandler

dotenv.load_dotenv()

# Устанавливаем формат лога в формате [дата и время] - [уровень лога] - [сообщение]
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


bot = Bot(os.getenv("TOKEN"))
dp = Dispatcher(storage=MemoryStorage())
db_handler = PostgresqlHandler()
db_video_handler = PostgresqlVideoHandler()
db_reminder_handler = PostgresqlRemindersHandler()


async def connect_to_db():
    # Устанавливаем название таблицы с данными пользователей
    await db_handler.set_table('users')

    # Подключаемся к БД Postgres
    await ParentPostgresqlHandler.open_connection(os.getenv('POSTGRES_CONNECTION_STRING'))

    # Создаем таблицы в базе данных если их нет
    await db_handler.create_table_if_not_exist()
    await db_video_handler.create_table_if_not_exist()
    await db_reminder_handler.create_table_if_not_exist()


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
