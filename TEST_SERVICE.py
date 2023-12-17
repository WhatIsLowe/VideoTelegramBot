from aiogram import Bot, Dispatcher, types
import asyncio
import logging
import os

import asyncpg
from aiogram.types import FSInputFile


async def upload_video(filepath: str, category_name: str):

    # await bot.send_video(chat_id=CHANNEL_ID, video=open(filepath, 'rb'))
    video = FSInputFile(filepath)
    message = await bot.send_video(chat_id=CHANNEL_ID, video=video)

    telegram_file_id = message.video.file_id
    print(telegram_file_id)

    conn = await asyncpg.connect(DSN)

    category_id = await conn.fetchval('SELECT id FROM categories WHERE name = $1', category_name)
    if category_id is None:
        await conn.execute('INSERT INTO categories (name) VALUES ($1)', category_name)
        category_id = await conn.fetchval('SELECT id FROM categories WHERE name = $1', category_name)

    await conn.execute('''
        INSERT INTO videos (category_id, telegram_file_id, name)
        VALUES ($1, $2, $3)''', category_id, telegram_file_id, os.path.basename(filepath))
    await conn.close()


async def main():
    await upload_video("C:/Users/vlad_/Downloads/котик.mp4", 'Жопа')

if __name__ == '__main__':
    TOKEN = "6877691480:AAEtX9Y3qnug970h0ycP04wSb0zFe9sNHrc"
    CHANNEL_ID = "-1002053511456"
    DSN = "postgres://postgres:2705071206@localhost:5432/postgres"

    bot = Bot(TOKEN)
    dp = Dispatcher()
    asyncio.run(main())

