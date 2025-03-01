from aiogram.filters import Filter
from aiogram.types import Message

from data.config import ADMINS


class IsCreate(Filter):
    async def __call__(self, message: Message) -> bool:
        return bool(message.from_user.id in ADMINS)
