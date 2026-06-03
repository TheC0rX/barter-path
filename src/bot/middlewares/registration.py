from typing import Any, Callable, Dict, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from cachetools import TTLCache

from src.db.repo import UserRepo


class RegistrationMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.reg_cache: Any = TTLCache(maxsize=20_000, ttl=3600)

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
        if user_id not in self.reg_cache:
            session = data.get("session")
            if session:
                user_repo = UserRepo(session)
                await user_repo.add_user(user_id, locale=str(tg_user.language_code))
                self.reg_cache[user_id] = True

        return await handler(event, data)
