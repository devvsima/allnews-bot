from aiogram import types
from aiogram.dispatcher.filters import Command, Text

from loader import dp, bot, _

from app.keyboards.inline.source import source_ikb, update_sources_ikb
from database.models import Users


@dp.message_handler(Command('source'))
@dp.message_handler(Text('🌐 Джерела'))
async def ask_sources(message: types.Message):
    user, created = Users.get_or_create(user_id=message.from_user.id)
    await message.reply("Виберіть джерела новин:", reply_markup=source_ikb(user))

# Обработчик нажатий на inline-кнопки для источников
@dp.callback_query_handler(Text(startswith=("source_")))
async def add_source(callback: types.CallbackQuery):
    source = callback.data.split("_")[1]
    user, created = Users.get_or_create(user_id=callback.from_user.id)
    sources = user.sources.split(', ') if user.sources else []
    if source not in sources:
        sources.append(source)
    else:
        sources.remove(source)
    user.sources = ', '.join(sources)
    user.save()
    await bot.answer_callback_query(callback.id, f"Джерела оновлено.")
    await update_sources(callback)

async def update_sources(callback: types.CallbackQuery):
    user = Users.get(Users.user_id == callback.from_user.id)
    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                text="Виберіть джерела новин:",
                                reply_markup=update_sources_ikb(user))
    
@dp.callback_query_handler(Text("save_sources"))
async def save_sources(callback: types.CallbackQuery):
    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                text="Ваш вибір збережено. Використовуйте команду /news для отримання новин або натисніть кнопку'🌐 Джерела'.",
                                reply_markup=None)