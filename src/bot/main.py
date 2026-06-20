from pathlib import Path
from loguru import logger

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores import FluentRuntimeCore
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import text

from src.services.updater import StalcraftUpdater

from src.bot.middlewares.i18n import UserLocaleManager
from src.bot.middlewares.errors import ErrorsMiddleware
from src.bot.middlewares.db import DbSessionMiddleware
from src.bot.middlewares.throttling import ThrottlingMiddleware
from src.bot.middlewares.registration import RegistrationMiddleware
from src.bot.handlers import setup_routers

from src.db.base import engine, async_session_maker
from src.config import config


async def check_db_connection() -> bool:
    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


async def main() -> None:
    if not await check_db_connection():
        logger.critical(f"[bold magenta][DB][/] Database is unavailable.")
        await engine.dispose()
        return

    bot = Bot(
        token=config.BOT_TOKEN.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    locales_path = Path(__file__).parent.parent / "locales"
    core = FluentRuntimeCore(path=str(locales_path / "{locale}"))

    i18n_middleware = I18nMiddleware(
        core=core,
        default_locale="en",
        manager=UserLocaleManager(),
    )

    i18n_middleware.setup(dp)

    for observer in (dp.message, dp.callback_query):
        observer.outer_middleware(ErrorsMiddleware())
        observer.outer_middleware(DbSessionMiddleware(async_session_maker))
        observer.outer_middleware(ThrottlingMiddleware())
        observer.outer_middleware(RegistrationMiddleware())

    dp.include_router(setup_routers())

    updater = StalcraftUpdater()
    scheduler = AsyncIOScheduler()

    @dp.startup()
    async def on_startup():
        await updater.check_and_update()

        scheduler.add_job(updater.check_and_update, "interval", hours=1)
        scheduler.start()
        logger.success("[bold magenta][BOT][/] Scheduler has been started.")
        logger.success("[bold magenta][BOT][/] The bot has been started.")

    @dp.shutdown()
    async def on_shutdown():
        logger.warning("[bold magenta][BOT][/] The bot is shutting down...")

        if scheduler.running:
            scheduler.shutdown()
            logger.info("[bold magenta][BOT][/] Scheduler has been stopped.")

        try:
            await updater.api.close()
            logger.info(
                "[bold magenta][API][/] Stalcraft API clients have been closed."
            )
        except Exception as e:
            logger.error(f"[bold magenta][API][/] Error closing Stalcraft API: {e}")

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

    except Exception as e:
        logger.exception(f"[bold magenta][BOT][/] Exception: \n{e}")

    finally:
        await engine.dispose()
        await bot.session.close()
        logger.info("[bold magenta][BOT][/] The bot has been stopped.")
