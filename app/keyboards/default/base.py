from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
from loader import _


def base_kb():
    kb = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton(text="🌐 Джерела"),
                KeyboardButton(text="✏️ Інтереси"),
            ],
            [
                KeyboardButton(text="📰 Новини"),
            ],
        ],
    )
    return kb

