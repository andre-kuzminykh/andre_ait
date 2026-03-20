"""
Точка входа Telegram-бота диагностики AI-зрелости.

## Трассируемость
Feature: F001 — AI Maturity Assessment

## Бизнес-контекст
Бот не обращается к БД напрямую — все операции
через REST API бэкенд-сервиса.
"""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from core.config import config
from handler.v1.user.assessment.F001.assessment_handler import router as assessment_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


async def main():
    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN is not set. Set it via environment variable or .env")
        sys.exit(1)

    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML"),
    )

    dp = Dispatcher()
    dp.include_router(assessment_router)

    logger.info("Bot starting... (API: %s)", config.api_url)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
