import logging
import sqlite3
from abc import ABC

from .base_database_handler import BaseDatabaseHandler


class SqliteHandler(BaseDatabaseHandler):
    def __init__(self):
        super().__init__()
        self._connection = None
        self._cursor = None

    async def set_table(self, table_name):
        """Определяет название таблицы базы данных.

        Название указывать без расширения ".db".
        :param table_name: Название таблицы.
        """
        self._table = table_name

    async def open_connection(self, dsn=None):
        """Создает соединение с таблицей базы данных.

        Принимает строку подключения к базе данных.
        Для SQLite dsn не нужно передавать, либо передать значение None.
        :param dsn: Connection arguments specified using as a single string in the following format: postgres://user:pass@host:port/database?option=value.
        """
        try:
            full_table_name = self._table + '.db'
            self._connection = sqlite3.connect(full_table_name)
            self._cursor = self._connection.cursor()
            logging.warning('Connected to sqlite database')
        except sqlite3.OperationalError as e:
            logging.error(f'Database connection error: {e}')

    async def close_connection(self):
        try:
            self._connection.commit()
            self._connection.close()
            logging.warning('Connection closed')
        except sqlite3.OperationalError as e:
            logging.error(f'Closing database connection error: {e}')

    async def create_table(self):
        try:
            self._cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self._table} (
            id INTEGER PRIMARY KEY,
            chat_id INTEGER UNIQUE NOT NULL,
            username TEXT NOT NULL,
            firstname TEXT,
            role Text NOT NULL)''')
            self._connection.commit()
            logging.warning('Table created successfully')
        except sqlite3.OperationalError as e:
            logging.error(f'Table creation error: {e}')

    async def insert_user(self, chat_id: int, username: str, firstname: str, role: str) -> None:
        try:
            self._cursor.execute(f'''INSERT INTO {self._table} (chat_id, username, firstname, role)
            VALUES (?, ?, ?, ?)''', (chat_id, username, firstname, role))
            self._connection.commit()
            logging.info(f'User {username} ({role}) was successfully added')
        except sqlite3.OperationalError as e:
            logging.error(f'Error while inserting user {username} ({role}): {e}')

    async def get_user(self, chat_id: int) -> tuple | None:
        try:
            result = self._cursor.execute(f'''SELECT * FROM {self._table} WHERE chat_id = ?''', (chat_id,))
            return result.fetchone()
        except sqlite3.OperationalError as e:
            logging.error(f'Error while fetching user {chat_id}')
