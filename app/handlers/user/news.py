from aiogram import types
from aiogram.dispatcher.filters import Command, Text

from loader import dp, bot, _

from database.models import Users
import feedparser

from aiogram.types import (
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
news_cache = {}
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
sources = [
        "Українська правда", "ТСН", "BBC Ukrainian", "Радіо Свобода",
        "Новое Время",
        "УНІАН", "Еспресо", "24 Канал",
        "BBC News", "CNN", "The New York Times", "The Guardian",
        "Al Jazeera", "The Washington Post"
]

# Команда /news для отправки новостей
@dp.message_handler(Command('news'))
@dp.message_handler(Text("📰 Новини"))
async def send_news(message: types.Message):
    user = Users.get(Users.user_id == message.from_user.id)
    if not user.sources:
        user.sources = "Українська правда, ТСН, BBC Ukrainian, Радіо Свобода, Новое Время, ЛІГА.net, Український Тиждень, Громадське, УНІАН, Еспресо, 24 Канал, Інтерфакс-Україна, BBC News, CNN, The New York Times, The Guardian, Reuters, Al Jazeera, Bloomberg, The Washington Post"
    if not user.interests:
        user.interests = "Політика 🏛️, Економіка 💰, Спорт ⚽, Технології 💻"


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
async def process_callback(callback: types.CallbackQuery):
    data = callback.data.split('_')
    action = data[0]
    index = int(data[1])
    user = Users.get(Users.user_id == callback.from_user.id)

    await bot.answer_callback_query(callback.id)  # Уведомление о том, что запрос обработан

    if action == 'next' or action == 'prev':
        news_list = news_cache.get(callback.message.chat.id)
        if news_list:
            if index < 0 or index >= len(news_list):
                await bot.edit_message_text(chat_id=callback.message.chat.id,
                                            message_id=callback.message.message_id,
                                            text="Більше новин немає.",
                                            reply_markup=None)
            else:
                news_item = news_list[index]
                text = f"Джерело: <blockquote>{news_item['source']}</blockquote>\nКатегорія: <blockquote>{news_item['category']}</blockquote>\n\n{news_item['title']}\n{news_item['link']}"
                markup = InlineKeyboardMarkup()
                next_button = InlineKeyboardButton('Наступна', callback_data=f'next_{index+1}')
                prev_button = InlineKeyboardButton('Попередня', callback_data=f'prev_{index-1}')
                markup.add(prev_button, next_button) if index > 0 else markup.add(next_button)

                await bot.edit_message_text(chat_id=callback.message.chat.id,
                                            message_id=callback.message.message_id,
                                            text=text,
                                            reply_markup=markup,
                                            parse_mode="HTML")