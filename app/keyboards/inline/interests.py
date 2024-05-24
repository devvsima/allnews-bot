from aiogram.types import (
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from loader import _


def interest_ikb(user):
    selected_interests = user.interests.split(', ') if user.interests else []
    markup = InlineKeyboardMarkup(row_width=1)
    categories = ["Політика 🏛️", "Економіка 💰", "Спорт ⚽", "Технології 💻"]
    for category in categories:
        text = f"{category} {'*' if category in selected_interests else ''}"
        markup.add(InlineKeyboardButton(text, callback_data=f"interest_{category}"))
    markup.add(InlineKeyboardButton("Готово", callback_data="save_interests"))
    return markup

def update_interests_ikb(user):
    selected_interests = user.interests.split(', ') if user.interests else []
    markup = InlineKeyboardMarkup(row_width=1)
    categories = ["Політика 🏛️", "Економіка 💰", "Спорт ⚽", "Технології 💻"]
    for category in categories:
        text = f"{category} {'*' if category in selected_interests else ''}"
        markup.add(InlineKeyboardButton(text, callback_data=f"interest_{category}"))
    markup.add(InlineKeyboardButton("Готово", callback_data="save_interests"))