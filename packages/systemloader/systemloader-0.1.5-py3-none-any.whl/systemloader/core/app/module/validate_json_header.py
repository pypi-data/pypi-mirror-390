from datetime import datetime
from typing import Union, Literal
from pydantic import BaseModel


class MessageHeader(BaseModel):
    reference_id: str
    message_id: str
    datetime_created: datetime
    api_version: str
    priority: Union[str, int]


class MessageHeaderCounter(MessageHeader):
    class Config:
        extra = 'allow'

    system_from: Literal['temp']
    system_to: Literal['mycounter']
    object: Literal['mycounter']
    action: Literal['get_counter']
