from typing import Any, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message

from data.config import ADMINS
from database.services.users import User


class AdminMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable, message: Message, data: dict) -> Any:
        session = data["session"]
        if user := await User.get(session, message.from_user.id):
            if user.id in ADMINS:
                data["user"] = user
                return await handler(message, data)
        return
