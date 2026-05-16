from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.bot import middlewares
from src.bot.handlers import setup_routers
from src.services.updater import StalcraftUpdater

from src.db.base import engine, async_session_maker
from src.config import config


async def main() -> None:
    bot = Bot(
        token=config.BOT_TOKEN.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    dp.update.outer_middleware(
        middlewares.DbSessionMiddleware(session_pool=async_session_maker)
    )
    middlewares.setup_i18n(dp)
    dp.include_router(setup_routers())

    updater = StalcraftUpdater()
    scheduler = AsyncIOScheduler()

    @dp.startup()
    async def on_startup():
        await updater.check_and_update()

        scheduler.add_job(updater.check_and_update, "interval", hours=1)
        scheduler.start()
        logger.info("Scheduler has been started.")

        logger.info("The bot has been started.")

    try:
        await bot.delete_webhook(True)
        await dp.start_polling(bot)

    except KeyboardInterrupt, SystemExit:
        logger.warning("The bot is shutting down...")
    except Exception as e:
        logger.exception(e)

    finally:
        scheduler.shutdown()
        logger.info("Scheduler has been stopped.")

        try:
            await updater.api.close()
            logger.info("Stalcraft API clients have been closed.")
        except Exception as e:
            logger.error(f"Error closing Stalcraft API: {e}")

        await engine.dispose()
        await bot.session.close()
        logger.info("The bot has been stopped.")
