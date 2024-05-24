from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
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
    message_id = IntegerField(null=True)  # Хранение ID последнего сообщения

db.connect()
db.create_tables([User])

# Глобальная переменная для хранения новостей
news_cache = {}

# Основная клавиатура
main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.add(KeyboardButton("🌐 Джерела"))
main_keyboard.add(KeyboardButton("✏️ Інтереси"))
main_keyboard.add(KeyboardButton("📰 Новини"))

# Команда /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    photo_path = r"D:\!010101010\Python\tg-bots\news\poster.webp"  # Замените на путь к локальному изображению

    caption = ("Привіт! Я новинний бот.\n Я допоможу тобі отримувати новини з різних джерел за твоїми інтересами.\n")
    with open(photo_path, 'rb') as photo:
        await bot.send_photo(chat_id=message.chat.id, photo=photo, caption=caption)
        await bot.send_message(chat_id=message.chat.id, text="В тебе з'явились кнопки, за допомогою них ти можеш обрати\
            категорію та джерело новин. Після цього можеш гортати новини з улюблених джерел!", reply_markup=main_keyboard)

# Команда /sources для изменения источников новостей
@dp.message_handler(text='🌐 Джерела')
async def ask_sources(message: types.Message):
    user, created = User.get_or_create(user_id=message.from_user.id)
    selected_sources = user.sources.split(', ') if user.sources else []
    markup = InlineKeyboardMarkup(row_width=1)
    sources = [
        "Українська правда", "ТСН", "BBC Ukrainian", "Радіо Свобода",
        "Новое Время",
        "УНІАН", "Еспресо", "24 Канал",
        "BBC News", "CNN", "The New York Times", "The Guardian",
        "Al Jazeera", "The Washington Post"
    ]
    for source in sources:
        text = f"{source} {'*' if source in selected_sources else ''}"
        markup.add(InlineKeyboardButton(text, callback_data=f"source_{source}"))
    markup.add(InlineKeyboardButton("Готово", callback_data="save_sources"))
    await message.reply("Виберіть джерела новин:", reply_markup=markup)

# Команда /interests для изменения категорий
@dp.message_handler(text='✏️ Інтереси')
async def ask_interests(message: types.Message):
    user, created = User.get_or_create(user_id=message.from_user.id)
    selected_interests = user.interests.split(', ') if user.interests else []
    markup = InlineKeyboardMarkup(row_width=1)
    categories = ["Політика 🏛️", "Економіка 💰", "Спорт ⚽", "Технології 💻"]
    for category in categories:
        text = f"{category} {'*' if category in selected_interests else ''}"
        markup.add(InlineKeyboardButton(text, callback_data=f"interest_{category}"))
    markup.add(InlineKeyboardButton("Готово", callback_data="save_interests"))
    await message.reply("Виберіть свої інтереси:", reply_markup=markup)

# Обработчик нажатий на inline-кнопки для источников
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
    await update_sources(callback_query)

async def update_sources(callback_query: types.CallbackQuery):
    user = User.get(User.user_id == callback_query.from_user.id)
    selected_sources = user.sources.split(', ') if user.sources else []
    markup = InlineKeyboardMarkup(row_width=1)
    sources = [
        "Українська правда", "ТСН", "BBC Ukrainian", "Радіо Свобода",
        "Новое Время",
        "УНІАН", "Еспресо", "24 Канал",
        "BBC News", "CNN", "The New York Times", "The Guardian",
        "Al Jazeera", "The Washington Post"
    ]
    for source in sources:
        text = f"{source} {'*' if source in selected_sources else ''}"
        markup.add(InlineKeyboardButton(text, callback_data=f"source_{source}"))
    markup.add(InlineKeyboardButton("Готово", callback_data="save_sources"))
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text="Виберіть джерела новин:",
                                reply_markup=markup)

# Обработчик нажатий на inline-кнопки для категорий
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
    await update_interests(callback_query)

async def update_interests(callback_query: types.CallbackQuery):
    user = User.get(User.user_id == callback_query.from_user.id)
    selected_interests = user.interests.split(', ') if user.interests else []
    markup = InlineKeyboardMarkup(row_width=1)
    categories = ["Політика 🏛️", "Економіка 💰", "Спорт ⚽", "Технології 💻"]
    for category in categories:
        text = f"{category} {'*' if category in selected_interests else ''}"
        markup.add(InlineKeyboardButton(text, callback_data=f"interest_{category}"))
    markup.add(InlineKeyboardButton("Готово", callback_data="save_interests"))
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text="Виберіть свої інтереси:",
                                reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data == "save_sources")
async def save_sources(callback_query: types.CallbackQuery):
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text="Ваш вибір збережено. Використовуйте команду /interests щоб обрати інтереси.",
                                reply_markup=None)

@dp.callback_query_handler(lambda c: c.data == "save_interests")
async def save_interests(callback_query: types.CallbackQuery):
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text="Ваш вибір збережено. Використовуйте команду /news для отримання новин.",
                                reply_markup=None)

# Команда /news для отправки новостей
@dp.message_handler(text="📰 Новини")
async def send_news(message: types.Message):
    user = User.get(User.user_id == message.from_user.id)
    if not user.sources:
        user.sources = "Українська правда, ТСН, BBC Ukrainian, Радіо Свобода, Новое Время, ЛІГА.net, Український Тиждень, Громадське, УНІАН, Еспресо, 24 Канал, Інтерфакс-Україна, BBC News, CNN, The New York Times, The Guardian, Reuters, Al Jazeera, Bloomberg, The Washington Post"
    if not user.interests:
        user.interests = "Політика 🏛️, Економіка 💰, Спорт ⚽, Технології 💻"
        sources = [
        "Українська правда", "ТСН", "BBC Ukrainian", "Радіо Свобода",
        "Новое Время",
        "УНІАН", "Еспресо", "24 Канал",
        "BBC News", "CNN", "The New York Times", "The Guardian",
        "Al Jazeera", "The Washington Post"
    ]
    news_feed = {
        "Українська правда": "https://www.pravda.com.ua/rss/",
        "ТСН": "https://tsn.ua/rss",
        "BBC Ukrainian": "http://www.bbc.com/ukrainian/index.xml",
        "Радіо Свобода": "https://www.radiosvoboda.org/api/zmgppemq$pp",
        "Новое Время": "https://nv.ua/ukr/rss/all.xml",
        "УНІАН": "https://rss.unian.net/site/news_ukr.rss",
        "Еспресо": "https://espreso.tv/rss",
        "24 Канал": "https://24tv.ua/rss/all.xml",
        "BBC News": "http://feeds.bbci.co.uk/news/rss.xml",
        "CNN": "http://rss.cnn.com/rss/edition.rss",
        "The New York Times": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "The Guardian": "https://www.theguardian.com/international/rss",
        "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
        "The Washington Post": "http://feeds.washingtonpost.com/rss/world"
    }
    await bot.send_message(message.from_user.id, '🔍 Пошук новин...')

    news_list = []
    for source in user.sources.split(', '):
        feed_url = news_feed.get(source)
        if feed_url:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:5]:
                news_list.append({
                    'title': entry.title,
                    'link': entry.link,
                    'source': source,
                    'category': user.interests
                })  # Обмежуємося 5 новинами з кожного джерела

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
    text = f"Джерело: <blockquote>{news_item['source']}</blockquote>\nКатегорія: <blockquote>{news_item['category']}</blockquote>\n\n{news_item['title']}\n{news_item['link']}"
    markup = InlineKeyboardMarkup()
    next_button = InlineKeyboardButton('Наступна', callback_data=f'next_{index+1}')
    prev_button = InlineKeyboardButton('Попередня', callback_data=f'prev_{index-1}')
    markup.add(prev_button, next_button) if index > 0 else markup.add(next_button)

    return await bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")

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
                text = f"Джерело: <blockquote>{news_item['source']}</blockquote>\nКатегорія: <blockquote>{news_item['category']}</blockquote>\n\n{news_item['title']}\n{news_item['link']}"
                markup = InlineKeyboardMarkup()
                next_button = InlineKeyboardButton('Наступна', callback_data=f'next_{index+1}')
                prev_button = InlineKeyboardButton('Попередня', callback_data=f'prev_{index-1}')
                markup.add(prev_button, next_button) if index > 0 else markup.add(next_button)

                await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                            message_id=callback_query.message.message_id,
                                            text=text,
                                            reply_markup=markup,
                                            parse_mode="HTML")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
