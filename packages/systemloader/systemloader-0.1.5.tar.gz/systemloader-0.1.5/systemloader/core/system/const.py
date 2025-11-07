from enum import Enum

ENGINE_VERSION = '1.0.1'


class MessageType(Enum):
    WEB = 'web'
    RABBITMQ = 'rabbitmq'
    CAMUNDA = 'camunda'


CHAT_NAMES = ('Bitrix24', 'Mattermost', 'Slack', 'Telegram', 'Zulip')
SPECIAL_FIELDS_ALERT_MESSAGE = ('exception', 'traceback')
