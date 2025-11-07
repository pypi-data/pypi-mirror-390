import redis
import orjson

from system.connection.BaseConnection import BaseConnection


class Redis(BaseConnection):
    def __init__(self, params):
        super().__init__(params)
        self.client = None

    async def connection(self):
        try:
            pool = redis.ConnectionPool(**self.values)
            self.client = redis.Redis(connection_pool=pool)
            if self.client.ping():
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
    def exists(self, *args):
        return self.client.exists(*args)

    # Записать каталог в Redis
    def set_dict(self, name_field: str, data):
        d = {
            name_field: orjson.dumps(data)
        }
        self.client.mset(d)

    # Установить данные Redis
    def set(self, name_field: str, value):
        self.client.set(name_field, value)

    # Получить данные из Redis
    def get(self, name_field: str):
        return self.client.get(name_field)

    # Удаление поля или полей
    def delete(self, *args):
        return self.client.delete(*args)

    # Установить значение на время жизни time в секундах
    def setex(self, name_field: str, time: int, value):
        return self.client.setex(name_field, time, value)

    # Установить на ключ время жизни
    def expire(self, *args):
        return self.client.expire(*args)

    # Добавить значение в очередь
    def lpush(self, key, *values):
        return self.client.lpush(key, *values)

    # Добавить значение в очередь
    def rpush(self, key, *values):
        return self.client.rpush(key, *values)

    # Достать значение из очереди
    def lpop(self, name):
        return self.client.lpop(name)

    # Достать значение из очереди
    def rpop(self, name):
        return self.client.rpop(name)

    # Получить информацию о глубине очереди
    def llen(self, key):
        return self.client.llen(key)

    # Добавить единицу к значению по ключу
    def incr(self, key, amount=1):
        return self.client.incr(key, amount)

    def decr(self, key, amount=1):
        return self.client.decr(key, amount)

    def execute_command(self, *args, **options):
        return self.client.execute_command(*args, **options)

    def persist(self, name):
        return self.client.persist(name)
