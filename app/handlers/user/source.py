from aiogram import types
from aiogram.dispatcher.filters import Command, Text

from loader import dp, bot, _

from data.config import DIR
from app.keyboards.inline.source import source_ikb
from database.models import Users


@dp.message_handler(Command('source'))
@dp.message_handler(Text('🌐 Джерела'))
async def ask_sources(message: types.Message):
    user, created = Users.get_or_create(user_id=message.from_user.id)
    await message.reply("Виберіть джерела новин:", reply_markup=source_ikb(user))
