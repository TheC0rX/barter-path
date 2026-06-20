from loguru import logger
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram_i18n import I18nContext


class ErrorsMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            i18n: I18nContext | None = data.get("i18n")
            error_text = (
                i18n.get("something-went-wrong") if i18n else "🤔 Something went wrong."
            )
            logger.exception(f"Error handling event {event.__class__.__name__}: {e}")

            if isinstance(event, CallbackQuery):
                await event.answer(error_text, show_alert=True)
            elif isinstance(event, Message):
                await event.reply(error_text)

            raise e
