from aiohttp import FormData

from system.connection.BaseConnection import BaseConnection
from system.module.AIOHttpSender import AIOHttpSender
from system.module.my_json import json_loads


class TelegramSender(BaseConnection):
    def __init__(self, params):
        super().__init__(params)
        self.url = f"https://api.telegram.org/bot{self.values['token_bot']}"
        self.chat_id = self.values['chat_id']
        self.sender = AIOHttpSender(self.logger, self.loop)

    async def connection(self):
        self.logger.info(f"Telegram API chat_id={self.chat_id} инициализирован!")
        return True

    async def send_message(self, text, parse_mode='html', user_id=None):
        res = await self.sender.post(f"{self.url}/sendMessage", data={
            'chat_id': user_id or self.chat_id,
            'text': text,
            'parse_mode': parse_mode,
        })
        return res

    async def send_photo(self, photo, text, parse_mode='html', user_id=None):
        form_data = FormData()
        form_data.add_field('chat_id', str(user_id or self.chat_id))
        form_data.add_field('caption', text)
        form_data.add_field('parse_mode', parse_mode),
        form_data.add_field('photo', photo, filename=None if isinstance(photo, str) else 'file.png'),
        res = await self.sender.post(f"{self.url}/sendPhoto", data=form_data)
        return res

    # Пользователь подписчик канала?
    async def get_chat_member(self, user_id: int, chat_id: int | str | None = None):
        status, response_json = await self.sender.post(f"{self.url}/getChatMember", data={
            'chat_id': chat_id or self.chat_id,
            'user_id': user_id,
        })
        response_dict = json_loads(response_json)
        return status and status < 300 and isinstance(response_dict, dict) and response_dict.get('ok'), response_dict
