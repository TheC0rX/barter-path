from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from src.bot.handlers import setup_routers
from src.bot.middlewares.i18n import setup_i18n

from src.config import config


async def main() -> None:
    bot = Bot(
        token=config.BOT_TOKEN.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    setup_i18n(dp)

    dp.include_router(setup_routers())

    try:
        await bot.delete_webhook(True)
        logger.info("The bot has been started.")

        await dp.start_polling(bot)

    except (KeyboardInterrupt, SystemExit):
        logger.warning("The bot is shutting down...")
    except Exception as e:
        logger.exception(e)

    finally:
        await bot.session.close()
        logger.info("The bot has been stopped.")
