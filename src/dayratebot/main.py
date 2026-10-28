import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from dayratebot.config import load_settings
from dayratebot.database import Database
from dayratebot.handlers import router


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = load_settings()
    database = Database(settings.database_path)
    await database.open()
    bot = Bot(token=settings.bot_token)
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher["database"] = database
    dispatcher.include_router(router)
    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()
        await database.close()


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run()
