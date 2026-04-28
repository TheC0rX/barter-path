from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repo import UserRepo

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, i18n: I18nContext, session: AsyncSession) -> None:
    repo = UserRepo(session)
    await repo.add_user(user_id=message.from_user.id, locale=i18n.locale)  # type: ignore

    await message.answer(i18n.get("start-welcome", name=message.from_user.first_name))  # type: ignore
