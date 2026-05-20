from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext

from src.bot.keyboard.callback_data import (
    MenuClick,
    MenuTaskNav,
    SearchItem,
    FinishTaskClick,
    AddTaskClick,
    RecipeNav,
    DeleteTaskClick,
    DiscountOfferClick,
    ActivateDiscountClick,
    ResourceClick,
    LanguageClick,
)


def get_main_menu_kb(
    i18n: I18nContext,
    has_tasks: bool,
    task_idx: int = 0,
    total_tasks: int = 0,
    current_task_id: int = 0,
    is_finished: bool = False,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if has_tasks and is_finished:
        builder.button(
            text=i18n.get("btn-finish_task"),
            callback_data=MenuClick(target="finish_task", task_id=current_task_id),
        )

    if has_tasks and total_tasks > 1:
        builder.button(text="⬅️", callback_data=MenuTaskNav(task_idx=task_idx - 1))
        builder.button(text="➡️", callback_data=MenuTaskNav(task_idx=task_idx + 1))

    builder.button(
        text=i18n.get("btn-add_task"),
        callback_data=MenuClick(target="add_task"),
    )

    if has_tasks:
        builder.button(
            text=i18n.get("btn-delete_task"),
            callback_data=MenuClick(target="delete_task", task_id=current_task_id),
        )
        builder.button(
            text=i18n.get("btn-activate_discount"),
            callback_data=MenuClick(
                target="activate_discount", task_id=current_task_id
            ),
        )
        builder.button(
            text=i18n.get("btn-manage_resources"),
            callback_data=MenuClick(target="manage_resources", task_id=current_task_id),
        )

    builder.button(
        text=i18n.get("btn-settings"),
        callback_data=MenuClick(target="settings"),
    )

    if has_tasks and total_tasks > 1:
        if is_finished:
            builder.adjust(1, 2, 2, 1)
        else:
            builder.adjust(2, 2, 1)
    elif has_tasks:
        if is_finished:
            builder.adjust(1, 2, 1)
        else:
            builder.adjust(2, 1)
    else:
        builder.adjust(1)

    return builder.as_markup()


def get_finish_task_kb(task_id: int, i18n: I18nContext) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=i18n.get("btn-confirm"),
        callback_data=FinishTaskClick(task_id=task_id),
    )
    builder.button(
        text=i18n.get("btn-cancel"),
        callback_data=MenuClick(target="main"),
    )
    builder.button(text=i18n.get("btn-back"), callback_data=MenuClick(target="main"))

    builder.adjust(2, 1)
    return builder.as_markup()


def get_back_button(i18n: I18nContext) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text=i18n.get("btn-back"), callback_data=MenuClick(target="main"))

    builder.adjust(1)
    return builder.as_markup()


def get_found_items_kb(items, i18n: I18nContext) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for item in items:
        display_name = item.name_ru if i18n.locale == "ru" else item.name_en
        builder.button(text=display_name, callback_data=SearchItem(item_id=item.id))

    builder.button(text=i18n.get("btn-back"), callback_data=MenuClick(target="main"))
    builder.adjust(1)

    return builder.as_markup()


def get_card_nav_kb(
    offer_idx: int,
    total_offers: int,
    item_id: str,
    i18n: I18nContext,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if total_offers > 1:
        prev_idx = (offer_idx - 1) % total_offers
        next_idx = (offer_idx + 1) % total_offers
        builder.button(
            text="⬅️", callback_data=RecipeNav(item_id=item_id, idx=str(prev_idx))
        )
        builder.button(
            text="➡️", callback_data=RecipeNav(item_id=item_id, idx=str(next_idx))
        )

    builder.button(
        text=i18n.get("btn-confirm"),
        callback_data=AddTaskClick(item_id=item_id, offer_idx=offer_idx),
    )

    builder.button(
        text=i18n.get("btn-back"),
        callback_data=MenuClick(target="add_task"),
    )

    if total_offers > 1:
        builder.adjust(2, 1)
    else:
        builder.adjust(1)

    return builder.as_markup()


def get_delete_task_kb(task_id: int, i18n: I18nContext) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=i18n.get("btn-confirm"),
        callback_data=DeleteTaskClick(task_id=task_id),
    )
    builder.button(
        text=i18n.get("btn-cancel"),
        callback_data=MenuClick(target="main"),
    )
    builder.button(text=i18n.get("btn-back"), callback_data=MenuClick(target="main"))

    builder.adjust(2, 1)
    return builder.as_markup()


def get_discount_offers_kb(task_id: int, i18n: I18nContext) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    discounts = [0, 10, 15, 20, 25, 30, 50, 75, 99]
    for d in discounts:
        builder.button(
            text=f"{d}%",
            callback_data=DiscountOfferClick(task_id=task_id, discount=d),
        )

    builder.button(text=i18n.get("btn-back"), callback_data=MenuClick(target="main"))

    builder.adjust(1)
    return builder.as_markup()


def get_activate_discount_kb(
    task_id: int, discount: int, i18n: I18nContext
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=i18n.get("btn-confirm"),
        callback_data=ActivateDiscountClick(task_id=task_id, discount=discount),
    )
    builder.button(
        text=i18n.get("btn-cancel"),
        callback_data=MenuClick(target="main"),
    )
    builder.button(text=i18n.get("btn-back"), callback_data=MenuClick(target="main"))

    builder.adjust(2, 1)
    return builder.as_markup()


def get_resources_management_kb(
    task_id: int,
    current_ings: list,
    progress_dict: dict,
    discount: int,
    i18n: I18nContext,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for ing_item, amount in current_ings:
        is_money = ing_item.id == "money"
        min_amount = 0 if is_money else 1
        discount_amount = max(min_amount, round(amount * (1 - discount / 100)))

        collected = progress_dict.get(ing_item.id, 0)
        display_collected = min(collected, discount_amount)

        name = ing_item.name_ru if i18n.locale == "ru" else ing_item.name_en

        icon = "✅" if display_collected == discount_amount else ing_item.icon
        button_text = f"{icon} {name} ({display_collected}/{discount_amount})"

        builder.button(
            text=button_text,
            callback_data=ResourceClick(
                action="select", task_id=task_id, ingredient_id=ing_item.id
            ),
        )
    builder.button(text=i18n.get("btn-back"), callback_data=MenuClick(target="main"))

    builder.adjust(1)
    return builder.as_markup()


def get_settings_kb(i18n: I18nContext) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    target_locale = "en" if i18n.locale == "ru" else "ru"
    builder.button(
        text=i18n.get("btn-switch_lang"),
        callback_data=LanguageClick(locale=target_locale),
    )
    builder.button(text=i18n.get("btn-back"), callback_data=MenuClick(target="main"))

    builder.adjust(1)
    return builder.as_markup()
