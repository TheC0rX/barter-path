from typing import Any, Dict, Callable, Awaitable

from aiogram import BaseMiddleware
from aiogram_i18n import I18nContext
from aiogram.types import Message, CallbackQuery, TelegramObject, InputRichMessage
from cachetools import TTLCache


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 0.6) -> None:
        super().__init__()
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
            i18n: I18nContext | None = data.get("i18n")

            if i18n:
                warning_msg = i18n.get("throttling-warning")
            else:
                warning_msg = "⌛ Slow down. Please wait a moment."

            if isinstance(event, CallbackQuery):
                await event.answer(warning_msg, show_alert=True)
            elif isinstance(event, Message):
                await event.reply_rich(rich_message=InputRichMessage(html=warning_msg))

            return

        self.cache[user_id] = True
        return await handler(event, data)
