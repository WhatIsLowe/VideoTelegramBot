import abc
from datetime import datetime

import asyncpg
import asyncio
import logging

from .base_database_handler import BaseDatabaseHandler


class ParentPostgresqlHandler:
    _pool = None

    # def __init__(self):
    #     self._pool = None

    @classmethod
    async def open_connection(cls, dsn: str):
        try:
            cls._pool = await asyncpg.create_pool(dsn)
            logging.info(f'Database Connection established')
        except Exception as e:
            logging.error(f'Could not connect to database: {e}')

    @classmethod
    async def close_connection(cls):
        try:
            await cls._pool.close()
            logging.info(f'Database Connection closed')
        except Exception as e:
            logging.error(f'Could not close database connection: {e}')

    @abc.abstractmethod
    async def create_table_if_not_exist(self):
        pass


class PostgresqlHandler(ParentPostgresqlHandler, BaseDatabaseHandler, abc.ABC):
    def __init__(self):
        super().__init__()
        # self._pool = None

    async def set_table(self, table_name: str):
        self._table = table_name


    async def create_table_if_not_exist(self):
        try:
            async with self._pool.acquire() as conn:
                async with conn.transaction():
                    await conn.execute(f'''
                    CREATE TABLE IF NOT EXISTS {self._table}
                    (id SERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL UNIQUE,
                    username VARCHAR(50) NOT NULL,
                    firstname VARCHAR(50) NOT NULL,
                    role VARCHAR(50) NOT NULL)''')
            logging.warning(f"Created table {self._table}")
        except asyncpg.exceptions.PostgresError as e:
            logging.error(f"Error creating table {self._table}: {e}")

    async def get_user_by_id(self, chat_id: int):
        try:
            async with self._pool.acquire() as conn:
                result = await conn.fetchrow(f"SELECT * FROM {self._table} WHERE chat_id = $1", chat_id)
            return result
        except asyncpg.exceptions.PostgresError as e:
            logging.error(f"Error getting user {chat_id}: {e}")

    async def get_user_by_username(self, username: str):
        try:
            async with self._pool.acquire() as conn:
                result = await conn.fetchrow(f"SELECT id, chat_id, username FROM {self._table} WHERE username = $1", username)
            return result
        except Exception as e:
            logging.error(f"Error getting user {username}: {e}")

    async def insert_user(self, chat_id: int, username: str, first_name: str, role: str):
        try:
            async with self._pool.acquire() as conn:
                await conn.execute(f'''INSERT INTO {self._table} (chat_id, username, firstname, role) 
                                       VALUES ($1, $2, $3, $4)''', chat_id, username, first_name, role)
            logging.warning(f"User {username} ({role}) was successfully inserted")
        except asyncpg.exceptions.PostgresError as e:
            logging.error(f"Error adding user {username} ({role}) to table {self._table}")
            logging.error(e)

    async def change_user_role(self, chat_id: int, new_role: str):
        try:
            async with self._pool.acquire() as conn:
                await conn.execute(f'''UPDATE {self._table} SET role=$1 WHERE chat_id=$2''', new_role, chat_id)
            logging.warning(f"User role changed to {new_role}")
        except asyncpg.exceptions.PostgresError as e:
            logging.error(f"Error changing user role to {new_role}")

    async def get_users_info(self):
        try:
            async with self._pool.acquire() as conn:
                result = await conn.fetchrow(f'''
                select count(*) as total_users,
                count(case when role='admin' then 1 end) as admin_users_count, 
                array_agg({self._table}) as admin_users_data, 
                count(case when role='user' then 1 end) as user_users_count 
                from {self._table}
                ''')
                logging.info(result)
            return result
        except asyncpg.exceptions.PostgresError as e:
            logging.error(f"Error getting users info from table {self._table}")
            logging.error(e)

    async def get_users(self):
        try:
            async with self._pool.acquire() as conn:
                result = await conn.fetch(f"select * from {self._table} where role='user'")
                return result
        except Exception as e:
            logging.error(f"Error getting users from table {self._table}: {e}")

class PostgresqlVideoHandler(ParentPostgresqlHandler):
    def __init__(self):
        super().__init__()
        # Установка названий таблиц базы данных
        self._video_table = 'videos'
        self._teachers_table = 'teachers'
        self._subjects_table = 'subjects'
        self._faculties_table = 'faculties'

    async def create_table_if_not_exist(self):
        try:
            async with self._pool.acquire() as conn:
                await conn.execute(f'''
                    CREATE TABLE IF NOT EXISTS {self._faculties_table}
                    (id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL);
                    
                    CREATE TABLE IF NOT EXISTS {self._subjects_table}
                    (id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    faculty_id INT REFERENCES {self._faculties_table}(id));
                    
                    CREATE TABLE IF NOT EXISTS {self._teachers_table}
                    (id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    subject_id INT REFERENCES {self._subjects_table}(id));
                    
                    CREATE TABLE IF NOT EXISTS {self._video_table}
                    (id SERIAL PRIMARY KEY,
                    teacher_id INT REFERENCES {self._teachers_table}(id),
                    telegram_file_id TEXT NOT NULL,
                    name TEXT NOT NULL);
                ''')
            logging.info(
                f"Tables {self._video_table}, {self._teachers_table}, {self._subjects_table}, {self._faculties_table} connected!")
        except asyncpg.exceptions.PostgresError as e:
            logging.error(f"Error creating tables: {e.args}")

    async def get_faculties(self):
        try:
            async with self._pool.acquire() as conn:
                result = await conn.fetch(f"SELECT * FROM {self._faculties_table}")
                return result
        except Exception as e:
            logging.error(f"Error getting faculties: {e}")

    async def get_subjects(self):
        try:
            async with self._pool.acquire() as conn:
                result = await conn.fetch(f"""SELECT S.id, S.name
                                              FROM {self._subjects_table} S
                                              JOIN {self._teachers_table} T ON S.id = T.subject_id
                                              JOIN {self._video_table} V ON T.id = V.teacher_id
                                              GROUP BY S.id, S.name
                                              HAVING COUNT(V.id) > 0""")
                return result
        except Exception as e:
            logging.error(f"Error getting subjects: {e}")

    async def get_teachers(self):
        try:
            async with self._pool.acquire() as conn:
                result = await conn.fetch(f"SELECT * FROM {self._teachers_table}")
                return result
        except Exception as e:
            logging.error(f"Error getting teachers: {e}")

    async def get_videos(self, category_id: int):
        try:
            async with self._pool.acquire() as conn:
                result = await conn.fetch(
                    f"SELECT id, name, telegram_file_id FROM {self._video_table} WHERE category_id = $1", category_id)
            return result
        except Exception as e:
            logging.error(f"Error getting videos by category_id {category_id}: {e}")

    async def get_videos_by_teacher_id(self, teacher_id: int):
        try:
            async with self._pool.acquire() as conn:
                result = await conn.fetch(
                    f"SELECT id, name, telegram_file_id FROM {self._video_table} WHERE teacher_id = $1", teacher_id)
            return result
        except Exception as e:
            logging.error(f"Error getting videos by teacher_id {teacher_id}: {e}")

    async def get_videos_by_subject_id(self, subject_id: int):
        try:
            async with self._pool.acquire() as conn:
                result = await conn.fetch(f"""SELECT V.id, V.name, V.telegram_file_id
                                              FROM {self._subjects_table} S
                                              JOIN {self._teachers_table} T ON S.id = T.subject_id
                                              JOIN {self._video_table} V ON T.id = V.teacher_id
                                              WHERE S.id = $1""", subject_id)
            return result
        except Exception as e:
            logging.error(f"Error getting videos by subject_id {subject_id}: {e}")

    async def get_videos_by_faculty_id(self, faculty_id: int):
        try:
            async with self._pool.acquire() as conn:
                result = await conn.fetch(f"""SELECT V.id, V.name, V.telegram_file_id
                                              FROM {self._faculties_table} F
                                              JOIN {self._subjects_table} S ON F.id = S.faculty_id
                                              JOIN {self._teachers_table} T ON S.id = T.subject_id
                                              JOIN {self._video_table} V ON T.id = V.teacher_id
                                              WHERE F.id = $1""", faculty_id)
            return result
        except Exception as e:
            logging.error(f"Error getting videos by faculty_id {faculty_id}: {e}")

    async def get_video_by_id(self, video_id: int):
        try:
            async with self._pool.acquire() as conn:
                result = await conn.fetchrow(
                    f"SELECT name, telegram_file_id FROM {self._video_table} WHERE id = $1", video_id)
                logging.info(f"Video with id {video_id}: {result}")
            return result
        except Exception as e:
            logging.error(f"Error getting video by ID. Video_id: {video_id}")
            logging.error(e)

    async def get_subject_id_by_video_id(self, video_id: int):
        try:
            async with self._pool.acquire() as conn:
                result = await conn.fetchrow(f"""SELECT S.id
                                                 FROM {self._subjects_table} S
                                                 JOIN {self._teachers_table} T ON S.id = T.subject_id
                                                 JOIN {self._video_table} V ON T.id = V.teacher_id
                                                 WHERE V.id = $1""", video_id)
            return result
        except Exception as e:
            logging.error(f"Error getting subject by video_id. Video_id: {video_id}, {e}")


class PostgresqlRemindersHandler(ParentPostgresqlHandler):
    def __init__(self):
        super().__init__()
        # Установка названий таблиц базы данных
        self._reminders_table = 'reminders'

    async def create_table_if_not_exist(self):
        try:
            async with self._pool.acquire() as conn:
                await conn.execute(f'''
                    CREATE TABLE IF NOT EXISTS {self._reminders_table}
                    (id SERIAL PRIMARY KEY,
                    username TEXT NOT NULL,
                    date_time TIMESTAMPTZ NOT NULL,
                    text TEXT NOT NULL);''')
            logging.info(f"Table {self._reminders_table} connected!")
        except Exception as e:
            logging.error(f"Error creating table {self._reminders_table}: {e}")

    async def add_reminder(self, username: str, date_time: datetime, text: str):
        try:
            async with self._pool.acquire() as conn:
                await conn.execute(f"""INSERT INTO {self._reminders_table} (username, date_time, text)
                                       VALUES ($1, $2, $3);""", username, date_time, text)
                logging.info(f"Added reminder: {username}, {date_time}, {text}")
        except Exception as e:
            logging.error(f"Error adding reminder: {username}, {date_time}, {text} | {e}")

    async def get_current_reminders(self):
        """ Возвращает напоминания на текущий момент """
        try:
            async with self._pool.acquire() as conn:
                reminders = await conn.fetch(f"SELECT * FROM {self._reminders_table} WHERE date_time AT TIME ZONE 'Europe/Moscow' <= NOW() AT TIME ZONE 'Europe/Moscow';")
            return reminders
        except Exception as e:
            logging.error(f"Error getting current reminders: {e}")

    async def delete_reminder(self, reminder_id: int):
        try:
            async with self._pool.acquire() as conn:
                await conn.execute(f"DELETE FROM {self._reminders_table} WHERE id = $1;", reminder_id)
            logging.info(f"Deleted reminder: {reminder_id}")
        except Exception as e:
            logging.error(f"Error deleting reminder: {reminder_id}")