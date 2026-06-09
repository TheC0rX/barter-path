from typing import Any

from aiogram.types import User
from aiogram_i18n.managers import BaseManager
from cachetools import TTLCache

from src.db.repo import UserRepo
from src.db.base import async_session_maker


class UserLocaleManager(BaseManager):
    def __init__(self):
        super().__init__()
        self.locale_cache: Any = TTLCache(maxsize=20_000, ttl=3600)

    async def get_locale(self, event_from_user: User) -> str:
        if not event_from_user:
            return self.default_locale

        user_id = event_from_user.id
        if user_id in self.locale_cache:
            return self.locale_cache[user_id]

        async with async_session_maker() as session:
            user_repo = UserRepo(session)
            db_locale = await user_repo.get_user_locale(user_id)

        user_lang = (
            db_locale or event_from_user.language_code or str(self.default_locale)
        )

        self.locale_cache[user_id] = user_lang
        return user_lang

    async def set_locale(self, locale: str, event_from_user: User) -> None:
        async with async_session_maker() as session:
            repo = UserRepo(session)
            await repo.update_user_locale(user_id=event_from_user.id, locale=locale)

        self.locale_cache[event_from_user.id] = locale
