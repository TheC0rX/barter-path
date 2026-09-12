from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from src.bot.utils.ui import show_main_menu

router = Router()


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    i18n: I18nContext,
    redis: Redis,
) -> None:
    await state.clear()
    await show_main_menu(message, session, i18n, redis)
