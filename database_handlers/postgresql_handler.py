import abc

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

    #
    # async def open_connection(self, dsn: str):
    #     try:
    #         self._pool = await asyncpg.create_pool(dsn)
    #     except Exception as e:
    #         logging.error("Could not open connection to PostgreSQL")
    #
    # async def close_connection(self):
    #     try:
    #         await self._pool.close()
    #         logging.info(f"PostgreSQL connection closed")
    #     except Exception as e:
    #         logging.error(f"Could not close connection to PostgreSQL")

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

    async def get_user(self, chat_id: int):
        try:
            async with self._pool.acquire() as conn:
                result = await conn.fetchrow(f"SELECT * FROM {self._table} WHERE chat_id = $1", chat_id)
            return result
        except asyncpg.exceptions.PostgresError as e:
            logging.error(f"Error getting user {chat_id}: {e}")

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


class PostgresqlVideoHandler(ParentPostgresqlHandler):
    def __init__(self):
        super().__init__()
        self._video_table = None
        self._categories_table = None

    async def set_video_table(self, video_table):
        self._video_table = video_table

    async def set_categories_table(self, categories_table):
        self._categories_table = categories_table

    async def create_table_if_not_exist(self):
        try:
            async with self._pool.acquire() as conn:
                await conn.execute(f'''
                    CREATE TABLE IF NOT EXISTS {self._categories_table}
                    (id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL);
                    
                    CREATE TABLE IF NOT EXISTS {self._video_table}
                    (id SERIAL PRIMARY KEY,
                    category_id INT REFERENCES {self._categories_table}(id),
                    telegram_file_id TEXT NOT NULL,
                    name TEXT NOT NULL);
                ''')
            logging.info(f"Tables {self._video_table}, {self._categories_table} connected")
        except asyncpg.exceptions.PostgresError as e:
            logging.error(f"Error creating tables: {e.args}")

    async def get_categories(self):
        try:
            async with self._pool.acquire() as conn:
                result = await conn.fetch(f"SELECT * FROM {self._categories_table}")
                return result
        except Exception as e:
            logging.error(f"Error getting categories: {e}")
    async def get_videos(self, category_id):
        try:
            async with self._pool.acquire() as conn:
                result = await conn.fetch(f"SELECT * FROM {self._video_table} WHERE category_id = $1", category_id)
            return result
        except Exception as e:
            logging.error(f"Error getting videos by category_id {category_id}: {e}")
