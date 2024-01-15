from aiogram import Bot, Dispatcher, types
import asyncio
import logging
import os

import asyncpg
from aiogram.types import FSInputFile

from dotenv import load_dotenv
load_dotenv()

async def upload_video(filepath: str, category_name: str):
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

async def upload_all_videos(directory: str, category_name: str):
    for filename in os.listdir(directory):
        if filename.endswith(".mp4"): 
            filepath = os.path.join(directory, filename)
            await upload_video(filepath, category_name)
            logging.info(f"File {filepath} uploaded!")

async def main():
    await upload_all_videos("", '')

if __name__ == '__main__':
    TOKEN = os.getenv('T_TOKEN')
    CHANNEL_ID = os.getenv('CHANNEL_ID')
    DSN = os.getenv('POSTGRES_CONNECTION_STRING')

    bot = Bot(TOKEN)
    dp = Dispatcher()
    asyncio.run(main())
