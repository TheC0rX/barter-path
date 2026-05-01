from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext

from src.bot.keyboard.callback_data import MenuClick, LanguageClick


def get_main_menu_kb(i18n: I18nContext) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="📝 " + i18n.get("buttons-add_task"),
        callback_data=MenuClick(target="add_task"),
    )
    builder.button(
        text="⚙️ " + i18n.get("buttons-settings"),
        callback_data=MenuClick(target="settings"),
    )

    builder.adjust(1)
    return builder.as_markup()


def get_back_button(i18n: I18nContext) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="⬅️ " + i18n.get("buttons-back"), callback_data=MenuClick(target="main")
    )

    builder.adjust(1)
    return builder.as_markup()


def get_settings_kb(i18n: I18nContext) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    target_locale = "en" if i18n.locale == "ru" else "ru"
    builder.button(
        text=i18n.get("settings-switch_lang"),
        callback_data=LanguageClick(locale=target_locale),
    )
    builder.button(
        text="⬅️ " + i18n.get("buttons-back"), callback_data=MenuClick(target="main")
    )

    builder.adjust(1)
    return builder.as_markup()
