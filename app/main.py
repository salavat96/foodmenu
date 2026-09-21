import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import settings
from app.data.seed_recipes import seed_recipes_if_empty
from app.database.session import init_models, session_scope
from app.handlers import get_root_router
from app.middlewares.antispam import AntiSpamMiddleware
from app.services.scheduler import setup_scheduler

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    await init_models()
    async with session_scope() as session:
        await seed_recipes_if_empty(session)

    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dispatcher = Dispatcher(storage=MemoryStorage())

    dispatcher.message.middleware(AntiSpamMiddleware())
    dispatcher.include_router(get_root_router())

    scheduler = setup_scheduler(bot)
    scheduler.start()

    try:
        await dispatcher.start_polling(bot)
    finally:
        scheduler.shutdown(wait=False)


if __name__ == "__main__":
    asyncio.run(main())
