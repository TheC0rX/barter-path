from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext

from src.bot.keyboard.callback_data import (
    MenuClick,
    MenuTaskNav,
    DeleteTaskClick,
    LanguageClick,
)


def get_main_menu_kb(
    i18n: I18nContext,
    has_tasks: bool,
    task_idx: int = 0,
    total_tasks: int = 0,
    current_task_id: int = 0,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if has_tasks and total_tasks > 1:
        builder.button(text="⬅️", callback_data=MenuTaskNav(task_idx=task_idx - 1))
        builder.button(text="➡️", callback_data=MenuTaskNav(task_idx=task_idx + 1))

    builder.button(
        text="📝 " + i18n.get("buttons-add_task"),
        callback_data=MenuClick(target="add_task"),
    )

    if has_tasks:
        builder.button(
            text="🗑️ " + i18n.get("buttons-delete_task"),
            callback_data=DeleteTaskClick(task_id=current_task_id),
        )

    builder.button(
        text="⚙️ " + i18n.get("buttons-settings"),
        callback_data=MenuClick(target="settings"),
    )

    if has_tasks and total_tasks > 1:
        builder.adjust(2, 2, 1)
    elif has_tasks:
        builder.adjust(2, 1)
    else:
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
