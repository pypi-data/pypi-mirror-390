import aiopyfcm
from aiopyfcm.errors import AioPyFCMError, InvalidCredentialsError, InternalServerError
from system.connection.BaseConnection import BaseConnection


class FirebasePush(BaseConnection):

    def __init__(self, params):
        super().__init__(params)
        self.credentials_file_path = self.values.get('credentials_file_path')
        self.authenticator = None

    @staticmethod
    def sample_authenticate(credentials_file_path: str):
        authenticator = aiopyfcm.PyFCMAuthenticator()
        authenticator.init_credentials_from_file(
            credentials_file_path=credentials_file_path,
            auto_refresh=True
        )
        return authenticator

    async def connection(self):
        try:
            self.authenticator = self.sample_authenticate(self.credentials_file_path)
            self.logger.info('PUSH Firebase подключен')
            return True
        except Exception as err:
            self.logger.error(f"PUSH Firebase не подключен ({err.__class__.__name__}: {err})")
            return False

    async def send_stateful(self, fmc_token: str, title: str, body: str, message_update: dict | None = None):
        async_pyfcm = aiopyfcm.AioPyFCM(self.authenticator)
        message = {
            'token': fmc_token,
            'notification': {
                'title': title,
                'body': body,
            }
        }
        if message_update:
            message |= message_update

        async with async_pyfcm as pyfcm:
            try:
                responses = await pyfcm.send(message)
                self.logger.debug(f"PUSH отправка {message=}\n{responses=}")
                return responses
            except (AioPyFCMError, InvalidCredentialsError, InternalServerError) as err:
                self.logger.error(f"{err.__class__.__name__}: {err}")
