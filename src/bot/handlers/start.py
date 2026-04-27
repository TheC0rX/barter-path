from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram_i18n import I18nContext

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, i18n: I18nContext) -> None:
    await message.answer(i18n.get("start-welcome", name=message.from_user.first_name))  # type: ignore
