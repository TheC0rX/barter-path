from pathlib import Path

from aiogram.types import User

from aiogram_i18n import I18nMiddleware
from aiogram_i18n.managers import BaseManager
from aiogram_i18n.cores import FluentRuntimeCore


class UserManager(BaseManager):
    async def get_locale(self, event_from_user: User) -> str:
        return (
            event_from_user.language_code
            if event_from_user.language_code in ["ru", "en"]
            else "en"
        )

    async def set_locale(self, locale: str) -> None:
        pass


def setup_i18n(dp) -> I18nMiddleware:
    locales_path = Path(__file__).parent.parent.parent / "locales"

    core = FluentRuntimeCore(path=str(locales_path / "{locale}"))
    middleware = I18nMiddleware(core=core, default_locale="en", manager=UserManager())

    middleware.setup(dp)
    return middleware
