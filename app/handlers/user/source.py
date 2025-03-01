from aiogram import F, types
from aiogram.filters import Command
from aiogram.filters.state import StateFilter

from app.handlers.msg_text import msg_text
from app.routers import user_router as router


@router.message(F.text == "🌐 Джерела'", StateFilter(None))
@router.message(Command("source"), StateFilter(None))
async def _source(message: types.Message) -> None:
    """ """
    await message.answer()
