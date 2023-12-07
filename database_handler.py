import logging
import sqlite3


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
