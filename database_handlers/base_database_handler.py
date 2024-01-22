from abc import ABC, abstractmethod


class BaseDatabaseHandler(ABC):
    def __init__(self):
        self._table = None

    @abstractmethod
    async def set_table(self, table_name: str) -> None:
        """Устанавливает таблицу базы данных в качестве рабочей.

        Указывать название таблицы необходимо в формате строки.
        :param table_name: Название таблицы.
        """
        pass

    @abstractmethod
    async def open_connection(self, dsn: str) -> None:
        """Создает соединение с таблицей базы данных.

        Принимает строку подключения к базе данных.
        :param dsn: Connection arguments specified using as a single string in the following format: postgres://user:pass@host:port/database?option=value.
        """
        pass

    @abstractmethod
    async def close_connection(self) -> None:
        """Закрывает соединение с базой данных.
        """
        pass

    @abstractmethod
    async def create_table_if_not_exist(self) -> None:
        """Создает таблицу в базе данных (если такой нет)

        Для корректной работы метода необходимо предварительно установить имя таблицы с помощью метода set_table.
        """
        pass

    @abstractmethod
    async def get_user_by_id(self, chat_id: int) -> tuple | None:
        """Получает данные пользователя из базы данных по его chat_id.

        Возвращает кортеж с данными пользователя если он найден, или None - если не найден.
        :param chat_id: ID чата пользователя.
        """
        pass

    @abstractmethod
    async def get_user_by_username(self, username: str) -> tuple | None:
        """Получает данные пользователя из базы данных по его username.

        Возвращает кортеж с данными пользователя если он найден, или None - если не найден.
        :param username: ID чата пользователя.
        """
        pass

    @abstractmethod
    async def insert_user(self, user_id: int, username: str, first_name: str, role: str) -> None:
        """Вставляет данные пользователя в базу данных.

        :param user_id: ID чата пользователя.
        :param username: Username пользователя.
        :param first_name: Имя пользователя в телеграм.
        :param role: Роль пользователя (admin | user)
        """
        pass

    @abstractmethod
    async def change_user_role(self, chat_id: int, new_role: str) -> None:
        """Позволяет поменять роль пользователя.

        :param chat_id: ID чата пользователя.
        :param new_role: Новая роль пользователя.
        """
        pass

    @abstractmethod
    async def get_users_info(self):
        """Возвращает список с данными о пользователях

        Такие данные:
            - Общее кол-во пользователей
            - Администраторы
            - Кол-во обычных пользователей
        :return:
        """
        pass