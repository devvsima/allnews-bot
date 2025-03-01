from aiogram import F, types
from aiogram.filters import Command
from aiogram.filters.state import StateFilter

from app.handlers.msg_text import msg_text
from app.routers import user_router as router


@router.message(F.text == "✏️ Інтереси", StateFilter(None))
@router.message(Command("interest"), StateFilter(None))
async def _help_command(message: types.Message) -> None:
    """ """
    await message.answer()
