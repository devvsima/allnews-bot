import asyncio

from aiogram.methods import DeleteWebhook

from app.handlers import setup_handlers
from app.middlewares import setup_middlewares
from app.others.commands import set_default_commands
from data.config import SKIP_UPDATES
from loader import bot, dp
from utils.logging import logger


async def on_startup() -> None:
    await set_default_commands()
    logger.info("~ Bot startup")


async def on_shutdown() -> None:
    logger.info("~ Bot shutting down...")


async def main():
    setup_middlewares(dp)
    setup_handlers(dp)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await bot(DeleteWebhook(drop_pending_updates=SKIP_UPDATES))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
