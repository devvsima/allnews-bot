from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from peewee import *
import feedparser

# Настройки бота
API_TOKEN = '6953757040:AAG1Jg5v_sSV3FTGEm7hgncTLVhb0ffL8c0'
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

# Настройки базы данных
db = SqliteDatabase('users.db')

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    user_id = IntegerField(unique=True)
    interests = TextField(null=True)
    sources = TextField(null=True)  # Хранение источников в виде строки

db.connect()
db.create_tables([User])

# Глобальная переменная для хранения новостей
news_cache = {}

# Команда /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    photo_url = "https://example.com/path/to/your/photo.jpg"  # Замените на URL вашей фотографии
    caption = ("Привіт! Я новинний бот. Я допоможу тобі отримувати новини за твоїми інтересами.\n"
               "Натисни кнопку нижче, щоб обрати джерела новин.")
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Обрати джерела новин", callback_data="choose_sources"))
    await bot.send_photo(chat_id=message.chat.id, photo=photo_url, caption=caption, reply_markup=markup)

# Обработчик нажатий на inline-кнопки
@dp.callback_query_handler(lambda c: c.data == "choose_sources")
async def choose_sources(callback_query: types.CallbackQuery):
    user, created = User.get_or_create(user_id=callback_query.from_user.id)
    selected_sources = user.sources.split(', ') if user.sources else []
    markup = InlineKeyboardMarkup(row_width=1)
    sources = ["Українська правда", "ТСН", "BBC Ukrainian", "Радіо Свобода"]
    for source in sources:
        text = f"{source} {'*' if source in selected_sources else ''}"
        markup.add(InlineKeyboardButton(text, callback_data=f"source_{source}"))
    markup.add(InlineKeyboardButton("Далі", callback_data="save_sources"))
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text="Виберіть джерела новин. Натисніть 'Далі' після вибору.",
                                reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data.startswith("source_"))
async def add_source(callback_query: types.CallbackQuery):
    source = callback_query.data.split("_")[1]
    user, created = User.get_or_create(user_id=callback_query.from_user.id)
    sources = user.sources.split(', ') if user.sources else []
    if source not in sources:
        sources.append(source)
    else:
        sources.remove(source)
    user.sources = ', '.join(sources)
    user.save()
    await bot.answer_callback_query(callback_query.id, f"Джерела оновлено.")
    await choose_sources(callback_query)  # Обновляем список источников

@dp.callback_query_handler(lambda c: c.data == "save_sources")
async def save_sources(callback_query: types.CallbackQuery):
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("Обрати інтереси", callback_data="choose_interests"))
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text="Ваш вибір збережено. Натисніть кнопку нижче, щоб обрати інтереси.",
                                reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data == "choose_interests")
async def choose_interests(callback_query: types.CallbackQuery):
    user, created = User.get_or_create(user_id=callback_query.from_user.id)
    selected_interests = user.interests.split(', ') if user.interests else []
    markup = InlineKeyboardMarkup(row_width=1)
    categories = ["Політика 🏛️", "Економіка 💰", "Спорт ⚽", "Технології 💻"]
    for category in categories:
        text = f"{category} {'*' if category in selected_interests else ''}"
        markup.add(InlineKeyboardButton(text, callback_data=f"interest_{category}"))
    markup.add(InlineKeyboardButton("Зберегти вибір", callback_data="save_interests"))
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text="Виберіть свої інтереси. Натисніть 'Зберегти вибір' після вибору.",
                                reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data.startswith("interest_"))
async def add_interest(callback_query: types.CallbackQuery):
    interest = callback_query.data.split("_")[1]
    user, created = User.get_or_create(user_id=callback_query.from_user.id)
    interests = user.interests.split(', ') if user.interests else []
    if interest not in interests:
        interests.append(interest)
    else:
        interests.remove(interest)
    user.interests = ', '.join(interests)
    user.save()
    await bot.answer_callback_query(callback_query.id, f"Інтереси оновлено.")
    await choose_interests(callback_query)  # Обновляем список интересов

@dp.callback_query_handler(lambda c: c.data == "save_interests")
async def save_interests(callback_query: types.CallbackQuery):
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text="Ваш вибір збережено. Використовуйте команду /news для отримання новин.",
                                reply_markup=None)

# Команда /news для отправки новостей
@dp.message_handler(commands=['news'])
async def send_news(message: types.Message):
    user = User.get(User.user_id == message.from_user.id)
    if not user.interests or not user.sources:
        await message.reply("Будь ласка, виберіть інтереси та джерела за допомогою команд /start та /sources.")
        return

    news_feed = {
        "Українська правда": "https://www.pravda.com.ua/rss/",
        "ТСН": "https://tsn.ua/rss",
        "BBC Ukrainian": "http://www.bbc.com/ukrainian/index.xml",
        "Радіо Свобода": "https://www.radiosvoboda.org/api/zmgppemq$pp",
    }

    news_list = []
    for source in user.sources.split(', '):
        feed_url = news_feed.get(source)
        if feed_url:
            feed = feedparser.parse(feed_url)
            news_list.extend(feed.entries[:5])  # Обмежуємося 5 новинами з кожного джерела

    news_cache[message.from_user.id] = news_list[:20]  # Обмежуємося 20 новинами в загальному списку

    if news_list:
        await message.reply(f"Знайдено {len(news_list)} новин(и).")
        sent_message = await send_news_item(message.chat.id, 0)
        user.message_id = sent_message.message_id
        user.save()
    else:
        await message.reply("Новини не знайдено.")

async def send_news_item(chat_id, index):
    news_list = news_cache.get(chat_id)
    if not news_list:
        return await bot.send_message(chat_id, "Новини не знайдено.")
    
    if index < 0 or index >= len(news_list):
        return await bot.send_message(chat_id, "Більше новин немає.")

    news_item = news_list[index]
    markup = InlineKeyboardMarkup()
    next_button = InlineKeyboardButton('Наступна', callback_data=f'next_{index+1}')
    prev_button = InlineKeyboardButton('Попередня', callback_data=f'prev_{index-1}')
    markup.add(prev_button, next_button) if index > 0 else markup.add(next_button)

    return await bot.send_message(chat_id, f"{news_item.title}\n{news_item.link}", reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data and (c.data.startswith('next_') or c.data.startswith('prev_')))
async def process_callback(callback_query: types.CallbackQuery):
    data = callback_query.data.split('_')
    action = data[0]
    index = int(data[1])
    user = User.get(User.user_id == callback_query.from_user.id)

    await bot.answer_callback_query(callback_query.id)  # Уведомление о том, что запрос обработан

    if action == 'next' or action == 'prev':
        news_list = news_cache.get(callback_query.message.chat.id)
        if news_list:
            if index < 0 or index >= len(news_list):
                await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                            message_id=callback_query.message.message_id,
                                            text="Більше новин немає.",
                                            reply_markup=None)
            else:
                news_item = news_list[index]
                markup = InlineKeyboardMarkup()
                next_button = InlineKeyboardButton('Наступна', callback_data=f'next_{index+1}')
                prev_button = InlineKeyboardButton('Попередня', callback_data=f'prev_{index-1}')
                markup.add(prev_button, next_button) if index > 0 else markup.add(next_button)

                await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                            message_id=callback_query.message.message_id,
                                            text=f"{news_item.title}\n{news_item.link}",
                                            reply_markup=markup)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
