from typing import Set, Dict, Any, List

import aiogram
from aiogram.types import video

from bot import db_handler, db_video_handler


async def write_user_in_db(callback: aiogram.types.CallbackQuery, role: str) -> None:
    """Передает данные пользователя в базу данных

    :param callback: колбэк
    :param role: роль пользователя
    """
    chat_id = callback.message.chat.id
    username = callback.from_user.username
    firstname = callback.from_user.first_name
    await db_handler.insert_user(chat_id=chat_id, username=username, first_name=firstname, role=role)


async def get_user_by_chat_id(chat_id: int) -> list | None:
    """Возвращает данные пользователя или None

    :param chat_id: id чата с пользователем
    :return: данные пользователя типа list или None - если не найден
    """
    result = await db_handler.get_user(chat_id=chat_id)
    return result


async def is_user_in_db(chat_id) -> bool:
    """Проверяет наличие пользователя в базе данных.

    :param chat_id: ID чата пользователя.
    :return: True или False в зависимости от результата.
    """
    user = await get_user_by_chat_id(chat_id)
    if user:
        return True
    else:
        return False


async def get_users_count() -> tuple:
    """Возвращает данные о количестве пользователей.


    :return:
    """
    # TODO: Сделать запрос кол-ва пользователей
    info = await db_handler.get_users_info()
    total_users = info['total_users']
    admin_users_count = info['admin_users_count']
    user_users_count = info['user_users_count']

    admin_users_data = info['admin_users_data']
    admin_usernames = [record['username'] for record in admin_users_data]
    return total_users, admin_users_count, admin_usernames, user_users_count
    pass


async def get_categories() -> dict:
    categories = await db_video_handler.get_categories()
    return {category["id"]: category["name"] for category in categories}


async def get_videos(category_id: int) -> list[dict[str, Any]]:
    videos = await db_video_handler.get_videos(category_id)
    return [{'id': vid['id'], 'name': vid['name'], 'file_id': vid['telegram_file_id']} for vid in videos]
