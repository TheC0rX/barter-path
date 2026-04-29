from aiogram import Router, F
from aiogram.types.callback_query import CallbackQuery
from aiogram_i18n import I18nContext

from src.bot.keyboard import inline
from src.bot.keyboard.callback_data import MenuClick

router = Router()


@router.callback_query(MenuClick.filter(F.target == "main"))
async def open_main_menu(callback: CallbackQuery, i18n: I18nContext) -> None:
    await callback.message.edit_text(  # type: ignore
        text=i18n.get("menu-main-text", name=callback.from_user.first_name),
        reply_markup=inline.get_main_menu_kb(i18n),
    )


@router.callback_query(MenuClick.filter(F.target == "settings"))
async def open_settings(callback: CallbackQuery, i18n: I18nContext) -> None:
    await callback.message.edit_text(  # type: ignore
        text=i18n.get("menu-settings-text"),
        reply_markup=inline.get_settings_kb(i18n),
    )
