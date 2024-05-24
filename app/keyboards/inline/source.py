from aiogram.types import (
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from loader import _

sources = [
        "Українська правда", "ТСН", "BBC Ukrainian", "Радіо Свобода",
        "Новое Время",
        "УНІАН", "Еспресо", "24 Канал",
        "BBC News", "CNN", "The New York Times", "The Guardian",
        "Al Jazeera", "The Washington Post"
]
    
def source_ikb(user):
    markup = InlineKeyboardMarkup(row_width=1)
    selected_sources = user.sources.split(', ') if user.sources else []
    for source in sources:
        text = f"{source} {'*' if source in selected_sources else ''}"
        markup.add(InlineKeyboardButton(text, callback_data=f"source_{source}"))
    markup.add(InlineKeyboardButton("Готово", callback_data="save_sources"))
    return markup

def update_sources_ikb(user):
    markup = InlineKeyboardMarkup(row_width=1)
    selected_sources = user.sources.split(', ') if user.sources else []
    for source in sources:
        text = f"{source} {'*' if source in selected_sources else ''}"
        markup.add(InlineKeyboardButton(text, callback_data=f"source_{source}"))
    markup.add(InlineKeyboardButton("Готово", callback_data="save_sources"))
    return markup