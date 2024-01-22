from datetime import datetime
from typing import Set, Dict, Any, List

import aiogram

from bot import db_handler, db_video_handler, db_reminder_handler


# === USER FUNCTIONS ===

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
    result = await db_handler.get_user_by_id(chat_id=chat_id)
    return result


async def get_user_by_username(username: str) -> dict | None:
    """Возвращает данные пользователя или None.

    :param username: Username пользователя.
    :return: Данные пользователя типа tuple или None - если не найден
    """
    user = await db_handler.get_user_by_username(username=username)
    if user:
        return {'id': user['id'], 'username': user['username'], 'chat_id': user['chat_id']}
    return None


async def is_user_in_db(chat_id=None, username=None) -> bool:
    """Проверяет наличие пользователя в базе данных.

    :param chat_id: ID чата пользователя.
    :param username: Username пользователя.
    :return: True или False в зависимости от результата.
    """
    if chat_id:
        user = await db_handler.get_user_by_id(chat_id)
    elif username:
        user = await db_handler.get_user_by_username(username)
    if user:
        return True
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


# === VIDEO FUNCTIONS ===

async def get_faculties() -> List[dict]:
    """ Возвращает список словарей факультетов.

    Словарь имеет вид: {'id': ID факультета, 'name': Название факультета}
    """
    faculties = await db_video_handler.get_faculties()
    return [{'id': faculty["id"], 'name': faculty["name"]} for faculty in faculties]


async def get_subjects() -> dict:
    """ Возвращает список словарей предметов кол-во видео по которым больше 0.

    Словарь имеет вид: {'id': ID предмета, 'name': Название предмета}
    """
    subjects = await db_video_handler.get_subjects()
    return {subject["id"]: subject["name"] for subject in subjects}


async def get_teachers() -> List[dict]:
    """ Возвращает список словарей преподавателей.

    Словарь имеет вид: {'id': ID преподавателя, 'name': ФИО преподавателя}
    """
    teachers = await db_video_handler.get_teachers()
    return [{'id': teacher["id"], 'name': teacher["name"]} for teacher in teachers]


async def get_videos_by_teacher(teacher_id: int) -> List[dict[str, Any]]:
    """ Возвращает список словарей видео по конкретному преподавателю.

    Словарь имеет следующий вид: {'id': ID видео, 'name': Название видео, 'file_id': ID файла в телеграм}.
    :param teacher_id: ID преподавателя в БД.
    """
    videos = await db_video_handler.get_videos_by_teacher_id(teacher_id=teacher_id)
    return [{'id': vid['id'], 'name': vid['name'], 'file_id': vid['telegram_file_id']} for vid in videos]


async def get_videos_by_subject(subject_id: int) -> List[dict[str, Any]]:
    """ Возвращает список словарей видео по предмету.

    Словарь имеет следующий вид: {'id': ID видео, 'name': Название видео, 'file_id': ID файла в телеграм}.
    :param subject_id: ID предмета в БД.
    """
    videos = await db_video_handler.get_videos_by_subject_id(subject_id=subject_id)
    return [{'id': vid['id'], 'name': vid['name'], 'file_id': vid['telegram_file_id']} for vid in videos]


async def get_videos_by_faculty(faculty_id: int) -> List[dict[str, Any]]:
    """ Возвращает список словарей видео по конкретному факультету.

    Словарь имеет следующий вид: {'id': ID видео, 'name': Название видео, 'file_id': ID файла в телеграм}.
    :param faculty_id: ID факультета в БД.
    """
    videos = await db_video_handler.get_videos_by_faculty_id(faculty_id=faculty_id)
    return [{'id': vid['id'], 'name': vid['name'], 'file_id': vid['telegram_file_id']} for vid in videos]


async def get_video(video_id: int) -> dict[str, Any]:
    """ Возвращает словарь с данными о видео.

    Словарь имеет следующий вид: {'name': Название видео, 'file_id': ID файла в телеграм}.
    :param video_id: ID видео в БД.
    """
    v = await db_video_handler.get_video_by_id(video_id)
    return {'name': v['name'], 'file_id': v['telegram_file_id']}


async def get_subject_id_by_video_id(video_id: int) -> int:
    """ Возвращает индекс предмета.

    Принимает индекс видео и возвращает индекс предмета.
    :param video_id: ID видео в БД.
    """
    subject_id = await db_video_handler.get_subject_id_by_video_id(video_id=video_id)
    return int(subject_id[0])


# === REMINDER FUNCTIONS ===

async def add_reminder(user: str, date_time: datetime, text: str) -> None:
    await db_reminder_handler.add_reminder(username=user, date_time=date_time, text=text)


async def delete_reminder(reminder_id: int) -> None:
    await db_reminder_handler.delete_reminder(reminder_id=reminder_id)

async def get_current_reminders():
    reminders = await db_reminder_handler.get_current_reminders()
    if reminders is None:
        return None
    return [{'id': reminder['id'], 'username': reminder['username'], 'text': reminder['text']} for reminder in reminders]