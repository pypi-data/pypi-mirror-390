import redis.asyncio as redis
import orjson

from system.connection.BaseConnection import BaseConnection


class RedisAsyncio(BaseConnection):
    def __init__(self, params):
        super().__init__(params)
        self.client = None

    async def connection(self):
        try:
            self.client = redis.Redis(**self.values)
            if await self.client.ping():
                self.logger.info('Redis подключен!')
                return True
            else:
                self.logger.error('Redis не пингуется!')
        except redis.ConnectionError as err:
            self.logger.error(f"Redis не подключен! Ошибка: {str(err)}")
        return False

    # Генерация ключа
    @staticmethod
    def gen_key(*args):
        return ':'.join(args)

    # Проверка на существование записи/записей
    async def exists(self, *args):
        return await self.client.exists(*args)

    # Записать каталог в Redis
    async def set_dict(self, name_field: str, data):
        d = {
            name_field: orjson.dumps(data)
        }
        await self.client.mset(d)

    # Установить данные Redis
    async def set(self, name_field: str, value):
        await self.client.set(name_field, value)

    # Получить данные из Redis
    async def get(self, name_field: str):
        return await self.client.get(name_field)

    # Удаление поля или полей
    async def delete(self, *args):
        return await self.client.delete(*args)

    # Установить значение на время жизни time в секундах
    async def setex(self, name_field: str, time: int, value):
        return await self.client.setex(name_field, time, value)

    # Установить на ключ время жизни
    async def expire(self, *args):
        return await self.client.expire(*args)

    # Добавить значение в очередь
    async def lpush(self, key, *values):
        return await self.client.lpush(key, *values)

    # Добавить значение в очередь
    async def rpush(self, key, *values):
        return await self.client.rpush(key, *values)

    # Достать значение из очереди
    async def lpop(self, name):
        return await self.client.lpop(name)

    # Достать значение из очереди
    async def rpop(self, name):
        return await self.client.rpop(name)

    # Получить информацию о глубине очереди
    async def llen(self, key):
        return await self.client.llen(key)

    # Добавить единицу к значению по ключу
    async def incr(self, key, amount=1):
        return await self.client.incr(key, amount)

    async def decr(self, key, amount=1):
        return await self.client.decr(key, amount)

    async def execute_command(self, *args, **options):
        return await self.client.execute_command(*args, **options)

    async def persist(self, name):
        return await self.client.persist(name)
