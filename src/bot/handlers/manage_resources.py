from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputRichMessage
from aiogram.fsm.context import FSMContext
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.keyboards import inline
from src.bot.utils.ui import show_main_menu
from src.bot.utils.states import ResourceCalcStates
from src.bot.keyboards.callback_data import (
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
    if not isinstance(callback.message, Message):
        await callback.answer()
        return

    user_id = callback.from_user.id
    task_id = callback_data.t_id
    ing_id = callback_data.ing_id

    user_repo = UserRepo(session)
    item_repo = ItemRepo(session)

    collected, discount_amount = await user_repo.get_resource_stats(
        user_id,
        task_id,
        ing_id,
    )
    remains = max(0, discount_amount - collected)
    unit = i18n.get("item_card-pieces", amount=discount_amount)
    ing_name = await item_repo.get_item_name_by_item_id(ing_id, i18n.locale)

    item = await user_repo.get_task_by_task_id(user_id, task_id)

    current_item = item.item
    item_icon = current_item.icon
    item_name = current_item.name_ru if i18n.locale == "ru" else current_item.name_en

    icon = "✅" if remains == 0 else "⌛"

    await state.update_data(
        task_id=task_id, ing_id=ing_id, remains=remains, collected=collected
    )
    await state.set_state(ResourceCalcStates.wait_for_amount)

    is_reset = True if remains < discount_amount else False
    await callback.message.edit_text(
        rich_message=InputRichMessage(html=f"""
                {i18n.get("manage_resources-placeholder")}

                <blockquote>
                {i18n.get("item_card-selected_item", icon=item_icon, item_name=item_name)}
                {i18n.get("ing_card-selected_item", ing_name=ing_name)}
                {i18n.get(
                    "ing_card-ing_progress",
                    icon=icon,
                    collected_amount=collected,
                    required_amount=discount_amount,
                    unit=unit
                )}
                {i18n.get("item_card-remains", amount=remains) if remains > 0 else ""}
                </blockquote>
                {i18n.get("type-resources") if remains > 0 else ""}
                {i18n.get("reset-description") if is_reset else ""}
            """),
        reply_markup=inline.get_resource_calc_kb(
            task_id,
            ing_id,
            i18n,
            is_reset=is_reset,
        ),
    )
    await callback.answer()


@router.message(ResourceCalcStates.wait_for_amount)
async def adding_resources(
    message: Message, state: FSMContext, session: AsyncSession, i18n: I18nContext
) -> None:
    if not message.from_user:
        return

    data = await state.get_data()
    task_id = data.get("task_id", 0)
    ing_id = data.get("ing_id", "")
    remains = data.get("remains", 0)

    if remains == 0:
        await message.answer_rich(
            rich_message=InputRichMessage(html=f"""
                    {i18n.get("manage_resources-placeholder")}

                    {i18n.get("resource-already-finished")}
                """),
            reply_markup=inline.get_resource_calc_kb(
                task_id,
                ing_id,
                i18n,
                is_reset=True,
            ),
        )
        return

    text = message.text.strip() if message.text else ""
    if not text.isdigit():
        await message.answer_rich(
            rich_message=InputRichMessage(html=f"""
                    {i18n.get("manage_resources-placeholder")}

                    {i18n.get("type-resources")}
                    {i18n.get("must-be-number")}
                """),
            reply_markup=inline.get_resource_calc_kb(task_id, ing_id, i18n),
        )
        return

    value_to_add = int(text)
    if value_to_add <= 0:
        await message.answer_rich(
            rich_message=InputRichMessage(html=f"""
                    {i18n.get("manage_resources-placeholder")}

                    {i18n.get("type-resources")}
                    {i18n.get("must-be-more-zero")}
                """),
            reply_markup=inline.get_resource_calc_kb(task_id, ing_id, i18n),
        )
        return

    if value_to_add >= 100_000_000:
        await message.answer_rich(
            rich_message=InputRichMessage(html=f"""
                    {i18n.get("manage_resources-placeholder")}

                    {i18n.get("type-resources")}
                    {i18n.get("must-be-less-limit")}
                """),
            reply_markup=inline.get_resource_calc_kb(task_id, ing_id, i18n),
        )
        return

    await state.clear()

    user_repo = UserRepo(session)
    item_repo = ItemRepo(session)

    ing_name = await item_repo.get_item_name_by_item_id(ing_id, i18n.locale)
    item_name = await user_repo.get_item_name_by_task_id(
        message.from_user.id,
        task_id,
        i18n.locale,
    )

    await message.answer_rich(
        rich_message=InputRichMessage(html=f"""
                {i18n.get("manage_resources-placeholder")}

                {i18n.get(
                    "adding_resources-confirmation",
                    amount=value_to_add,
                    ing_name=ing_name,
                    item_name=item_name,
                )}
            """),
        reply_markup=inline.get_update_resources_kb(
            task_id, ing_id, value_to_add, i18n
        ),
    )


@router.callback_query(ResourceCalc.filter(F.action == ResourceCalcAction.RESET))
async def reset_resources(
    callback: CallbackQuery,
    callback_data: ResourceCalc,
    state: FSMContext,
    session: AsyncSession,
    i18n: I18nContext,
) -> None:
    if not isinstance(callback.message, Message):
        await callback.answer()
        return

    await state.clear()

    user_id = callback.from_user.id
    task_id = callback_data.t_id
    ing_id = callback_data.ing_id

    user_repo = UserRepo(session)
    item_repo = ItemRepo(session)

    ing_name = await item_repo.get_item_name_by_item_id(ing_id, i18n.locale)
    item_name = await user_repo.get_item_name_by_task_id(user_id, task_id, i18n.locale)

    await callback.message.edit_text(
        rich_message=InputRichMessage(html=f"""
                {i18n.get("manage_resources-placeholder")}

                {i18n.get(
                    "reset_resources-confirmation",
                    ing_name=ing_name,
                    item_name=item_name,
                )}
            """),
        reply_markup=inline.get_update_resources_kb(task_id, ing_id, -1, i18n),
    )
    await callback.answer()


@router.callback_query(ResourceCalc.filter(F.action == ResourceCalcAction.CONFIRM))
async def update_resources(
    callback: CallbackQuery,
    callback_data: ResourceCalc,
    session: AsyncSession,
    i18n: I18nContext,
) -> None:
    if not isinstance(callback.message, Message):
        await callback.answer()
        return

    user_id = callback.from_user.id
    task_id = callback_data.t_id
    ing_id = callback_data.ing_id
    value = callback_data.val

    user_repo = UserRepo(session)

    if value == -1:
        await user_repo.reset_resource_amount(user_id, task_id, ing_id)
    else:
        await user_repo.add_resource_amount(user_id, task_id, ing_id, value)

    await callback.answer(
        text=i18n.get("update_resources-updated"),
        show_alert=False,
    )

    await show_main_menu(callback, session, i18n, task_id=task_id)
