from aiogram import Router, F
from aiogram.types.callback_query import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.keyboard import inline
from src.bot.utils.states import ResourceCalcStates
from src.bot.keyboard.callback_data import (
    ResourceClick,
    ResourceCalc,
    ResourceCalcAction,
)
from src.db.repo import UserRepo, ItemRepo

router = Router()


@router.callback_query(ResourceClick.filter())
async def process_resource_selection(
    callback: CallbackQuery,
    callback_data: ResourceClick,
    state: FSMContext,
    session: AsyncSession,
    i18n: I18nContext,
) -> None:
    task_id = callback_data.task_id
    ing_id = callback_data.ing_id

    user_repo = UserRepo(session)
    item_repo = ItemRepo(session)

    collected, discount_amount = await get_resource_stats(
        task_id, ing_id, user_repo, item_repo
    )
    ing_remaining = max(0, discount_amount - collected)

    ingredient = await item_repo.get_item(ing_id)
    ing_name = ingredient.name_ru if i18n.locale == "ru" else ingredient.name_en
    item_name = await user_repo.get_item_name_by_task_id(task_id, i18n.locale)

    is_money = ingredient.id == "money"
    icon = "💵" if is_money else "⌛"

    await state.update_data(task_id=task_id, ing_id=ing_id, remains=ing_remaining)
    await state.set_state(ResourceCalcStates.wait_for_amount)

    await callback.message.edit_text(  # type: ignore
        text=i18n.get("manage_resources-placeholder")
        + "\n\n"
        + i18n.get("type-resources")
        + "\n\n"
        + f"{i18n.get("item_card-selected_item", item_name=item_name)}\n"
        + f"{ingredient.icon if ingredient is not None else ""} {i18n.get("ing_card-selected_item", ing_name=ing_name)}\n"
        + f"{icon} {i18n.get(
            "ing_card-ing_progress",
            collected_amount=collected,
            required_amount=discount_amount,
        )}\n"
        + f"└ {i18n.get("item_card-remains", amount=ing_remaining)}"
        + "\n\n"
        + i18n.get("reset-description"),
        reply_markup=inline.get_resource_calc_kb(task_id, ing_id, i18n),
    )
    await callback.answer()


@router.callback_query(ResourceCalc.filter(F.action == ResourceCalcAction.RESET))
async def reset_resources(
    callback: CallbackQuery,
    callback_data: ResourceCalc,
    session: AsyncSession,
    i18n: I18nContext,
) -> None:
    task_id = callback_data.task_id
    ing_id = callback_data.ing_id

    user_repo = UserRepo(session)
    item_repo = ItemRepo(session)
    ingredient = await item_repo.get_item(ing_id)
    ing_name = ingredient.name_ru if i18n.locale == "ru" else ingredient.name_en
    item_name = await user_repo.get_item_name_by_task_id(task_id, i18n.locale)

    await callback.message.edit_text(  # type: ignore
        text=i18n.get("manage_resources-placeholder")
        + "\n\n"
        + i18n.get(
            "reset_resources-confirmation", ing_name=ing_name, item_name=item_name
        ),
        reply_markup=inline.get_update_resources_kb(task_id, ing_id, 0, i18n),
    )
    await callback.answer()


async def get_resource_stats(
    task_id: int, ing_id: str, user_repo: UserRepo, item_repo: ItemRepo
) -> tuple[int, int]:
    task = await user_repo.get_task_by_task_id(task_id)
    rows = await item_repo.get_item_recipes(task.item_id)
    progress_dict = await user_repo.get_task_progress_dict(task_id)

    found_ing = next(
        (
            (ing, r.amount)
            for r, ing in rows
            if r.offer_index == task.offer_idx and ing.id == ing_id
        ),
        None,
    )
    if not found_ing:
        return 0, 0

    ing_item, base_amount = found_ing
    is_money = ing_item.id == "money"
    discount_amount = max(
        0 if is_money else 1, round(base_amount * (1 - task.discount / 100))
    )

    return min(progress_dict.get(ing_id, 0), discount_amount), discount_amount
