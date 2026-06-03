from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram_i18n import I18nContext

from src.bot.keyboard import inline
from src.bot.keyboard.callback_data import LanguageClick

router = Router()


@router.callback_query(LanguageClick.filter())
async def change_language(
    callback: CallbackQuery, callback_data: LanguageClick, i18n: I18nContext
) -> None:
    if not isinstance(callback.message, Message):
        await callback.answer()
        return

    await i18n.set_locale(callback_data.locale)

    await callback.message.edit_text(
        text=f"{i18n.get("settings-placeholder")}\n___"
        + "\n\n"
        + i18n.get("settings-language_changed"),
        reply_markup=inline.get_settings_kb(i18n),
    )
    await callback.answer()
