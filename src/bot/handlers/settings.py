from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.utils.ui import show_main_menu
from src.bot.keyboards.callback_data import LanguageClick

router = Router()


@router.callback_query(LanguageClick.filter())
async def change_language(
    callback: CallbackQuery,
    callback_data: LanguageClick,
    session: AsyncSession,
    i18n: I18nContext,
) -> None:
    if not isinstance(callback.message, Message):
        await callback.answer()
        return

    task_id = callback_data.t_id

    await i18n.set_locale(callback_data.loc)
    await callback.answer(
        text=i18n.get("settings-language_changed"),
        show_alert=False,
    )

    await show_main_menu(callback, session, i18n, task_id=task_id)
