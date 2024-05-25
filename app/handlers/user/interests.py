from aiogram import types
from aiogram.dispatcher.filters import Command, Text

from loader import dp, bot, _

from app.keyboards.inline.interests import interest_ikb, update_interests_ikb
from database.models import Users


@dp.message_handler(Command('interest'))
@dp.message_handler(Text('✏️ Інтереси'))
async def ask_interests(message: types.Message):
    user, created = Users.get_or_create(user_id=message.from_user.id)
    await message.reply("Виберіть свої інтереси:", reply_markup=interest_ikb(user))
    
# Обработчик нажатий на inline-кнопки для категорий
@dp.callback_query_handler(Text(startswith="interest_"))
async def add_interest(callback: types.CallbackQuery):
    interest = callback.data.split("_")[1]
    user, created = Users.get_or_create(user_id=callback.from_user.id)
    interests = user.interests.split(', ') if user.interests else []
    if interest not in interests:
        interests.append(interest)
    else:
        interests.remove(interest)
    user.interests = ', '.join(interests)
    user.save()
    await bot.answer_callback_query(callback.id, f"Інтереси оновлено.")
    await update_interests(callback)

async def update_interests(callback: types.CallbackQuery):
    user = Users.get(Users.user_id == callback.from_user.id)
    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                text="Виберіть свої інтереси:",
                                reply_markup=update_interests_ikb(user))

@dp.callback_query_handler(Text("save_interests"))
async def save_interests(callback: types.CallbackQuery):
    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                text="Ваш вибір збережено. Використовуйте команду /news для отримання новин або натисніть кнопку'🌐 Джерела'.",
                                reply_markup=None)