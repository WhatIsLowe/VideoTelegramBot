# Модуль для кэширования данных из БД
import logging

import aioredis


class RedisCache:
    """Класс для кэширования данных в Redis
    """
    def __init__(self):
        self.redis_cache = None

    async def init_cache(self):
        self.redis_cache = await aioredis.Redis(host='localhost', port=6379, decode_responses=True)
        logging.info('Redis Cache initialized')

    async def get(self, key):
        """Получить данные из кэша по ключу

        :param key: ключ
        :return: значение ключа или None
        """
        val = await self.redis_cache.get(key)
        logging.info(f'Из кэша редис были запрошены данные по ключу {key}')
        return val

    async def set(self, key, value) -> bool:
        """Сохраняет данные в кэше Redis

        :param key: ключ
        :param value: значение
        :return: boolean
        """
        state = await self.redis_cache.set(key, value)
        logging.info(f'В редис кэш добавлены данные с ключом {key}')
        return state
