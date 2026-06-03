from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.utils.ui import show_main_menu

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, i18n: I18nContext, session: AsyncSession) -> None:
    await show_main_menu(message, session, i18n)
