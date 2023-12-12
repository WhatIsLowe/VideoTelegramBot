import aiogram
from bot import db_handler


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
    user = await get_user_by_chat_id(chat_id)
    if user:
        return True
    else:
        return False

async def get_users_count() -> list:
    # TODO: Сделать запрос кол-ва пользователей
    pass