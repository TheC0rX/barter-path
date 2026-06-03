from typing import Any, Dict, Callable, Awaitable

from aiogram import BaseMiddleware
from aiogram_i18n import I18nMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from cachetools import TTLCache

from src.bot.middlewares.i18n import UserLocaleManager


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(
        self,
        i18n_middleware: I18nMiddleware,
        rate_limit: float = 0.6,
    ) -> None:
        super().__init__()
        self.i18n = i18n_middleware
        self.locale_manager: UserLocaleManager = i18n_middleware.manager  # type: ignore
        self.cache: Any = TTLCache(maxsize=10_000, ttl=rate_limit)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, (Message, CallbackQuery)):
            return await handler(event, data)

        tg_user = event.from_user
        if not tg_user or tg_user.is_bot:
            return await handler(event, data)

        user_id = tg_user.id
        if user_id in self.cache:
            locale = await self.locale_manager.get_locale(tg_user)
            warning_msg = self.i18n.core.get("throttling-warning", locale=locale)

            if isinstance(event, CallbackQuery):
                await event.answer(warning_msg, show_alert=True)
            elif isinstance(event, Message):
                await event.reply(text=warning_msg)

            return

        self.cache[user_id] = True
        return await handler(event, data)
