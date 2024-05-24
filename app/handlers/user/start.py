from aiogram import types
from aiogram.dispatcher.filters import CommandStart

from loader import dp, bot, _

from data.config import DIR
from app.keyboards.default import base_kb


@dp.message_handler(CommandStart())
async def send_welcome(message: types.Message):
    photo_path = f"{DIR}\images\poster.webp" 

    caption = ("Привіт! Я новинний бот.\n Я допоможу тобі отримувати новини з різних джерел за твоїми інтересами.\n")
    with open(photo_path, 'rb') as photo:
        await bot.send_photo(chat_id=message.chat.id, photo=photo, caption=caption)
        await bot.send_message(chat_id=message.chat.id, text="В тебе з'явились кнопки, за допомогою них ти можеш обрати\
            категорію та джерело новин. Після цього можеш гортати новини з улюблених джерел!", reply_markup=base_kb())
