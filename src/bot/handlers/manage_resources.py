from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
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


@router.message(ResourceCalcStates.wait_for_amount)
async def additing_resources(
    message: Message, state: FSMContext, session: AsyncSession, i18n: I18nContext
) -> None:
    text = message.text.strip() if message.text else ""
    if not text.isdigit():
        await message.answer(
            text=i18n.get("manage_resources-placeholder")
            + "\n\n"
            + i18n.get("must-be-number"),
            reply_markup=inline.get_back_button(i18n),
        )
        return

    value_to_add = int(text)
    if value_to_add <= 0:
        await message.answer(
            text=i18n.get("manage_resources-placeholder")
            + "\n\n"
            + i18n.get("must-be-more-zero"),
            reply_markup=inline.get_back_button(i18n),
        )
        return

    data = await state.get_data()
    task_id = data.get("task_id", 0)
    ing_id = data.get("ing_id", "")
    remains = data.get("remains", 0)

    if remains == 0:
        await message.answer(
            text=i18n.get("manage_resources-placeholder")
            + "\n\n"
            + i18n.get("resource-already-finished"),
            reply_markup=inline.get_back_button(i18n),
        )
        await state.clear()
        return

    user_repo = UserRepo(session)
    item_repo = ItemRepo(session)

    ingredient = await item_repo.get_item(ing_id)
    ing_name = ingredient.name_ru if i18n.locale == "ru" else ingredient.name_en  # type: ignore
    item_name = await user_repo.get_item_name_by_task_id(task_id, i18n.locale)

    collected, _ = await get_resource_stats(task_id, ing_id, user_repo, item_repo)

    await message.answer(
        text=i18n.get("manage_resources-placeholder")
        + "\n\n"
        + i18n.get(
            "additing_resources-confirmation",
            amount=value_to_add,
            ing_name=ing_name,
            item_name=item_name,
        ),
        reply_markup=inline.get_update_resources_kb(
            task_id, ing_id, collected + value_to_add, i18n
        ),
    )
    await state.clear()


@router.callback_query(ResourceCalc.filter(F.action == ResourceCalcAction.RESET))
async def reset_resources(
    callback: CallbackQuery,
    callback_data: ResourceCalc,
    state: FSMContext,
    session: AsyncSession,
    i18n: I18nContext,
) -> None:
    if await state.get_state():
        await state.clear()

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


@router.callback_query(ResourceCalc.filter(F.action == ResourceCalcAction.CONFIRM))
async def update_resources(
    callback: CallbackQuery,
    callback_data: ResourceCalc,
    session: AsyncSession,
    i18n: I18nContext,
) -> None:
    task_id = callback_data.task_id
    ing_id = callback_data.ing_id
    value = callback_data.value

    user_repo = UserRepo(session)
    await user_repo.update_resource_amount(task_id, ing_id, value)

    await callback.message.edit_text(  # type: ignore
        text=i18n.get("manage_resources-placeholder")
        + "\n\n"
        + i18n.get("update_resources-updated"),
        reply_markup=inline.get_back_button(i18n),
    )
    await callback.answer()


async def get_resource_stats(
    task_id: int,
    ing_id: str,
    user_repo: UserRepo,
    item_repo: ItemRepo,
) -> tuple[int, int]:
    task = await user_repo.get_task_by_task_id(task_id)
    rows = await item_repo.get_item_recipes(task.item_id)
    progress_dict = await user_repo.get_task_progress_dict(task_id)

    found_ing = next(
        (
            (recipe, ing)
            for recipe, ing in rows
            if recipe.offer_index == task.offer_idx and ing.id == ing_id
        ),
        None,
    )
    if not found_ing:
        return 0, 0

    recipe, ing_item = found_ing
    is_money = ing_item.id == "money"
    min_amount = 0 if is_money else 1

    discount_amount = max(min_amount, round(recipe.amount * (1 - task.discount / 100)))
    display_collected = min(progress_dict.get(ing_id, 0), discount_amount)

    return display_collected, discount_amount
