from aiogram.types import (
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from loader import _


async def source_ikb(user):
    ikb = InlineKeyboardMarkup(
        resize_keyboard=True,
        inline_keyboard=[
            [
                InlineKeyboardButton(text="click", callback_data="callback"),
            ],
        ],
    )
    markup = InlineKeyboardMarkup(row_width=1)
    sources = [
        "Українська правда", "ТСН", "BBC Ukrainian", "Радіо Свобода",
        "Новое Время",
        "УНІАН", "Еспресо", "24 Канал",
        "BBC News", "CNN", "The New York Times", "The Guardian",
        "Al Jazeera", "The Washington Post"
    ]
    selected_sources = user.sources.split(', ') if user.sources else []
    
    for source in sources:
        text = f"{source} {'*' if source in selected_sources else ''}"
        markup.add(InlineKeyboardButton(text, callback_data=f"source_{source}"))
    markup.add(InlineKeyboardButton("Готово", callback_data="save_sources"))
    return ikb