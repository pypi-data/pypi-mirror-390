from dadata import DadataAsync, settings
from httpx import HTTPError, HTTPStatusError

from system.connection.BaseConnection import BaseConnection


def client_context(fnc):
    async def wrapper(*args, **kwargs):
        self = args[0]
        async with DadataAsync(self.token, self.secret) as dadata:
            try:
                return await fnc(self, dadata, *args[1:], **kwargs)
            except (HTTPError, HTTPStatusError) as err:
                self.logger.error(f"{err.__class__.__name__}: {err}")
                return
    return wrapper


class Dadata(BaseConnection):
    def __init__(self, params):
        super().__init__(params)
        self.token, self.secret = self.values['token'], self.values['secret']

    async def connection(self):
        self.logger.info("Dadata подключена!")
        return True

    # Организация по ИНН или ОГРН (https://dadata.ru/api/find-party/)
    @client_context
    async def find_by_id(self, dadata, name: str, query: str, count: int = settings.SUGGESTION_COUNT, **kwargs):
        result = await dadata.find_by_id(name, query, count, **kwargs)
        return result

    # подсказки по организациям
    @client_context
    async def suggest(self, dadata, name: str, query: str, count: int = settings.SUGGESTION_COUNT, **kwargs):
        result = await dadata.suggest(name, query, count, **kwargs)
        return result
