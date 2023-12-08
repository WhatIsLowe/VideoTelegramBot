import logging
import sqlite3
import asyncpg
import asyncio


class SQLiteHandler:
    def __init__(self):
        self._conn = None
        self._cursor = None
        self._table = None

    def set_table(self, table_name: str):
        self._table = table_name

    def open_connection(self):
        try:
            full_table_name = self._table + '.db'
            self._conn = sqlite3.connect(full_table_name)
            self._cursor = sqlite3.Cursor(self._conn)
            logging.warning(f"База {self._table} подключена!")
        except Exception as e:
            logging.error(f"Ошибка при подключении базы {self._table}: {e}")

    def close_connection(self):
        try:
            self._conn.commit()
            self._conn.close()
            logging.warning("Соединение с базой закрыто!")
        except Exception as e:
            logging.error(f"Не удалось закрыть соединение с базой из-за ошибки: {e}")

    def create_table(self):
        try:
            self._cursor.execute(f'''CREATE TABLE {self._table}
                                   (id INTEGER PRIMARY KEY,
                                    chat_id INTEGER UNIQUE NOT NULL,
                                    username TEXT NOT NULL,
                                    firstname TEXT,
                                    role TEXT NOT NULL)''')

            self._conn.commit()
            logging.warning(f"База {self._table} успешно создана!")
        except sqlite3.OperationalError:
            logging.error(f"Не удалось создать базу {self._table}. База с таким названием уже существует!")

    def write_user(self, chat_id: int, username: str, firstname: str, role: str):
        try:
            self._cursor.execute(f'''INSERT INTO {self._table} (chat_id, username, firstname, role) 
            values (?, ?, ?, ?)''', (chat_id, username, firstname, role))
            self._conn.commit()
            logging.info(f"Пользователь {username} ({role}) успешно занесен в базу!")
        except Exception as e:
            logging.error(f"Не удалось занести пользователя {username} в базу, из-за ошибки: {e}")

    def select_user(self, chat_id: int) -> list | None:
        try:
            result = self._cursor.execute(f'''SELECT * FROM {self._table} WHERE chat_id=?''', (chat_id,))
            return result.fetchone()
        except Exception as e:
            logging.error(f"Не удалось получить данные пользователя с chat_id: {chat_id}!")


class PostrgreSQLHandler:
    def __init__(self):
        self._pool = None
        self._table = None

    async def set_table(self, table_name: str):
        self._table = table_name

    async def open_connection(self, dsn: str):
        try:
            self._pool = await asyncpg.create_pool(dsn)
            logging.warning(f"Соединение с базой PostgreSQL установлено для таблицы {self._table}")
        except Exception as e:
            logging.error(f"Не удалось установить соединение с базой PostgreSQL, таблицей {self._table}")

    async def close_connection(self):
        try:
            await self._pool.close()
            logging.warning(f"Соединение с PostgreSQL базой, таблицей {self._table} закрыто!")
        except Exception as e:
            logging.error(f"Не удалось закрыть соединение с PostgreSQL базой, таблицей {self._table}")

    async def create_table(self):
        try:
            async with self._pool.acquire() as connection:
                async with connection.transaction():
                    await connection.execute(f'''CREATE TABLE IF NOT EXISTS {self._table}
                                                (id SERIAL PRIMARY KEY,
                                                chat_id BIGINT UNIQUE NOT NULL,
                                                username TEXT NOT NULL,
                                                firstname TEXT,
                                                role TEXT NOT NULL)''')
                    logging.warning(f"Таблица {self._table} в базе PostgreSQL создана!")
        except asyncpg.exceptions.PostgresError as e:
            logging.error(f"Ошибка при создании талицы {self._table} в PostrgreSQL базе: {e}")

    async def write_user(self, chat_id: int, username: str, firstname: str, role: str):
        try:
            async with self._pool.acquire() as connection:
                await connection.execute(f'''INSERT INTO {self._table} (chat_id, username, firstname, role)
                                            VALUES ($1, $2, $3, $4)''', chat_id, username, firstname, role)
            logging.info(f"Пользователь {username} ({role}) успешно добавлен в БД")
        except Exception as e:
            logging.error(f"Ошибка при внесении пользователя в БД: {e}")

    async def select_user(self, chat_id: int):
        try:
            async with self._pool.acquire() as connection:
                query = f'SELECT * FROM {self._table} WHERE chat_id = $1'
                result = await connection.fetchrow(query, chat_id)
            return result
        except Exception as e:
            logging.error(f"Не удалось получить данные пользователя по chat_id: {chat_id}. Причина: {e}")


# === DEBUG ===
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    db = SQLiteHandler()
    db.set_table('users')
    db.open_connection()
    # db.create_table()
    db.write_user(chat_id=1488, username='whatislove', firstname='Vladushka', role='admin')
    user = db.select_user(chat_id=1337)
    if user:
        print(type(user))
        print(*user)
    else:
        print("Пользователь не обнаружен!")
    db.close_connection()
