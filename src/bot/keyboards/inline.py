from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext

from src.bot.keyboards.callback_data import (
    MenuClick,
    MenuNav,
    FinishTaskClick,
    AddTaskClick,
    DeleteTaskClick,
    DiscountClick,
    ResourceClick,
    ResourceCalc,
    LanguageClick,
)
from src.bot.keyboards.callback_data import (
    MenuAction,
    DiscountAction,
    AddTaskAction,
    ResourceCalcAction,
)


def add_back_button(
    builder: InlineKeyboardBuilder,
    i18n: I18nContext,
    target: MenuAction = MenuAction.MENU,
    task_id: int = 0,
) -> InlineKeyboardMarkup:
    builder.row(
        InlineKeyboardButton(
            text=i18n.get("btn-back"),
            callback_data=MenuClick(target=target, t_id=task_id).pack(),
        )
    )
    return builder.as_markup()


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
            callback_data=MenuClick(
                target=MenuAction.FINISH_TASK, t_id=current_task_id
            ),
        )

    if has_tasks and total_tasks > 1:
        builder.button(
            text="⬅️",
            callback_data=MenuNav(idx=task_idx - 1),
        )
        builder.button(
            text=f"{task_idx + 1}/{total_tasks}",
            callback_data="ignore",
        )
        builder.button(
            text="➡️",
            callback_data=MenuNav(idx=task_idx + 1),
        )

    builder.button(
        text=i18n.get("btn-add_task"),
        callback_data=MenuClick(target=MenuAction.ADD_TASK),
    )

    if has_tasks:
        builder.button(
            text=i18n.get("btn-delete_task"),
            callback_data=MenuClick(
                target=MenuAction.DELETE_TASK, t_id=current_task_id
            ),
        )
        builder.button(
            text=i18n.get("btn-activate_discount"),
            callback_data=MenuClick(
                target=MenuAction.ACTIVATE_DISCOUNT, t_id=current_task_id
            ),
        )
        builder.button(
            text=i18n.get("btn-manage_resources"),
            callback_data=MenuClick(
                target=MenuAction.MANAGE_RESOURCES, t_id=current_task_id
            ),
        )

    builder.button(
        text=i18n.get("btn-settings"),
        callback_data=MenuClick(target=MenuAction.SETTINGS),
    )

    if has_tasks and total_tasks > 1:
        if is_finished:
            builder.adjust(1, 3, 2, 1)
        else:
            builder.adjust(3, 2, 1)
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
        callback_data=FinishTaskClick(t_id=task_id),
    )

    builder.adjust(1)
    return add_back_button(builder, i18n)


def get_back_button(i18n: I18nContext) -> InlineKeyboardMarkup:
    return add_back_button(InlineKeyboardBuilder(), i18n)


def get_found_items_kb(
    items,
    i18n: I18nContext,
    prev_id: str = "",
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for item in items:
        display_name = item.name_ru if i18n.locale == "ru" else item.name_en
        builder.button(
            text=display_name,
            callback_data=AddTaskClick(
                action=AddTaskAction.SEARCH, item_id=item.id, prev_id=prev_id
            ),
        )

    builder.adjust(1)
    return add_back_button(builder, i18n)


def get_card_nav_kb(
    offer_idx: int,
    total_offers: int,
    item_id: str,
    i18n: I18nContext,
    prev_id: str = "",
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=i18n.get("btn-confirm"),
        callback_data=AddTaskClick(
            action=AddTaskAction.CONFIRM,
            item_id=item_id,
            o_idx=offer_idx,
            prev_id=prev_id,
        ),
    )

    if total_offers > 1:
        prev_idx = (offer_idx - 1) % total_offers
        next_idx = (offer_idx + 1) % total_offers
        builder.button(
            text="⬅️",
            callback_data=AddTaskClick(
                action=AddTaskAction.NAVIGATION,
                item_id=item_id,
                idx=prev_idx,
                prev_id=prev_id,
            ),
        )
        builder.button(
            text=f"{offer_idx + 1}/{total_offers}",
            callback_data="ignore",
        )
        builder.button(
            text="➡️",
            callback_data=AddTaskClick(
                action=AddTaskAction.NAVIGATION,
                item_id=item_id,
                idx=next_idx,
                prev_id=prev_id,
            ),
        )

    if total_offers > 1:
        builder.adjust(1, 3, 1)
    else:
        builder.adjust(1)

    return add_back_button(
        builder,
        i18n,
        target=MenuAction.MENU if prev_id else MenuAction.ADD_TASK,
    )


def get_delete_task_kb(task_id: int, i18n: I18nContext) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=i18n.get("btn-confirm"),
        callback_data=DeleteTaskClick(t_id=task_id),
    )

    builder.adjust(1)
    return add_back_button(builder, i18n)


def get_discount_offers_kb(task_id: int, i18n: I18nContext) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    discounts = [0, 10, 15, 20, 25, 30, 50, 75, 99]
    for d in discounts:
        builder.button(
            text=f"{d}%",
            callback_data=DiscountClick(
                action=DiscountAction.OFFER,
                t_id=task_id,
                dc=d,
            ),
        )

    builder.adjust(3)
    return add_back_button(builder, i18n)


def get_activate_discount_kb(
    task_id: int,
    discount: int,
    i18n: I18nContext,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=i18n.get("btn-confirm"),
        callback_data=DiscountClick(
            action=DiscountAction.CONFIRM,
            t_id=task_id,
            dc=discount,
        ),
    )

    builder.adjust(1)
    return add_back_button(
        builder,
        i18n,
        target=MenuAction.ACTIVATE_DISCOUNT,
        task_id=task_id,
    )


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
            callback_data=ResourceClick(t_id=task_id, ing_id=ing_item.id),
        )

    builder.adjust(1)
    return add_back_button(builder, i18n)


def get_resource_calc_kb(
    task_id: int, ing_id: str, i18n: I18nContext
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=i18n.get("btn-reset"),
        callback_data=ResourceCalc(
            action=ResourceCalcAction.RESET,
            t_id=task_id,
            ing_id=ing_id,
        ),
    )

    builder.adjust(1)
    return add_back_button(
        builder,
        i18n,
        target=MenuAction.MANAGE_RESOURCES,
        task_id=task_id,
    )


def get_update_resources_kb(
    task_id: int, ing_id: str, value: int, i18n: I18nContext
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=i18n.get("btn-confirm"),
        callback_data=ResourceCalc(
            action=ResourceCalcAction.CONFIRM,
            t_id=task_id,
            ing_id=ing_id,
            val=value,
        ),
    )

    builder.adjust(1)
    return add_back_button(
        builder,
        i18n,
        target=MenuAction.MANAGE_RESOURCES,
        task_id=task_id,
    )


def get_settings_kb(i18n: I18nContext) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    target_locale = "en" if i18n.locale == "ru" else "ru"
    builder.button(
        text=i18n.get("btn-switch_lang"),
        callback_data=LanguageClick(loc=target_locale),
    )

    builder.adjust(1)
    return add_back_button(builder, i18n)
