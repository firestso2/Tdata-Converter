"""
Session Exporter Bot
====================
Author: @vorache777

Entry point – wires aiogram + FSM + all routers together.
"""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import load_config
from handlers.start import router as start_router
from handlers.auth import router as auth_router
from handlers.download import router as download_router

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    config = load_config()

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Register routers (order matters — more specific first)
    dp.include_router(start_router)
    dp.include_router(auth_router)
    dp.include_router(download_router)

    logger.info("Starting Session Exporter Bot…")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
