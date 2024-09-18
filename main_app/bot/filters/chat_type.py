from aiogram.types import Message,ContentType
from aiogram.filters import Filter
from aiogram.filters import BaseFilter


class chat_type_filter(Filter):
    def __init__(self,chat_types:list[str]) -> None:
        self.chat_types = chat_types

    async def __call__(self,message:Message) -> bool:
        return message.chat.type in self.chat_types


class MediaFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        file = message.content_type in [ContentType.PHOTO, ContentType.DOCUMENT]
        return file if file else 'False'