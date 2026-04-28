from pathlib import Path

from aiogram.types import User

from aiogram_i18n import I18nMiddleware
from aiogram_i18n.managers import BaseManager
from aiogram_i18n.cores import FluentRuntimeCore

from src.db.repo import UserRepo
from src.db.base import async_session_maker


class UserManager(BaseManager):
    async def get_locale(self, event_from_user: User) -> str:
        async with async_session_maker() as session:
            repo = UserRepo(session)
            user = await repo.get_user(event_from_user.id)

            if user:
                return user.locale

        return (
            event_from_user.language_code
            if event_from_user.language_code in ["ru", "en"]
            else "en"
        )

    async def set_locale(self, locale: str, event_from_user: User) -> None:
        async with async_session_maker() as session:
            repo = UserRepo(session)
            await repo.add_user(user_id=event_from_user.id, locale=locale)


def setup_i18n(dp) -> I18nMiddleware:
    locales_path = Path(__file__).parent.parent.parent / "locales"

    core = FluentRuntimeCore(path=str(locales_path / "{locale}"))
    middleware = I18nMiddleware(core=core, default_locale="en", manager=UserManager())

    middleware.setup(dp)
    return middleware
