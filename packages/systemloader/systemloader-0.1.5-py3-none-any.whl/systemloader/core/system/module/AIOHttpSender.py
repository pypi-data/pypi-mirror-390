from aiohttp import ClientSession, TCPConnector, BasicAuth
import asyncio
import aiohttp

HEADERS = {'charset': 'UTF-8'}


def errors_not_connection(fnc):
    async def wrapper(*args, **kwargs):
        self = args[0]
        try:
            return await fnc(*args, **kwargs)
        except (aiohttp.client_exceptions.ClientConnectorError,
                asyncio.exceptions.TimeoutError, aiohttp.client_exceptions.ServerDisconnectedError) as err:
            self.logger.error(f"{err.__class__.__name__}: {err}")
        return None, None
    return wrapper


class AIOHttpSender:
    def __init__(self, logger, loop, headers=None, basic_auth_dict=None, proxy=None, proxy_auth_dict=None):
        self.loop = loop
        self.logger = logger
        self.headers = headers or HEADERS
        self.basic_auth = BasicAuth(basic_auth_dict['login'], basic_auth_dict['password']) if basic_auth_dict else None
        self.proxy = proxy
        self.proxy_auth = BasicAuth(proxy_auth_dict['login'], proxy_auth_dict['password']) if proxy_auth_dict else None

    @errors_not_connection
    async def get(self, url, params=None, headers=None, response_text=True, ssl_verify=True):
        async with ClientSession(
                headers=headers or self.headers, connector=None if ssl_verify else TCPConnector(ssl=False),
                auth=self.basic_auth, proxy=self.proxy, proxy_auth=self.proxy_auth, loop=self.loop) as session:
            async with session.get(url, params=params) as response:
                return response.status, await response.text() if response_text else await response.content.read()

    @errors_not_connection
    async def post(self, url, data, headers=None, response_text=True, ssl_verify=True):
        async with ClientSession(
                headers=headers or self.headers, connector=None if ssl_verify else TCPConnector(ssl=False),
                auth=self.basic_auth, proxy=self.proxy, proxy_auth=self.proxy_auth, loop=self.loop) as session:
            async with session.post(url, data=data) as response:
                return response.status, await response.text() if response_text else await response.content.read()
