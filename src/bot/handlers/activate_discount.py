from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.utils.ui import render_item_card
from src.bot.keyboards import inline
from src.bot.keyboards.callback_data import DiscountClick, DiscountAction
from src.db.repo import UserRepo

router = Router()


@router.callback_query(DiscountClick.filter(F.action == DiscountAction.OFFER))
async def process_discount_selection(
    callback: CallbackQuery,
    callback_data: DiscountClick,
    session: AsyncSession,
    i18n: I18nContext,
) -> None:
    if not isinstance(callback.message, Message):
        await callback.answer()
        return

    user_id = callback.from_user.id
    task_id = callback_data.t_id
    discount = callback_data.dc

    repo = UserRepo(session)
    current_task = await repo.get_task_by_task_id(user_id, task_id)

    card_text, _, _ = await render_item_card(
        user_id,
        current_task.item_id,
        current_task.offer_idx,
        session,
        i18n,
        discount=discount,
    )

    await callback.message.edit_text(
        text=f"{i18n.get("activate_discount-placeholder")}\n___"
        + "\n\n"
        + i18n.get("discount-preview", discount=discount)
        + "\n\n"
        + card_text,
        reply_markup=inline.get_activate_discount_kb(
            task_id=task_id, discount=discount, i18n=i18n
        ),
    )
    await callback.answer()


@router.callback_query(DiscountClick.filter(F.action == DiscountAction.CONFIRM))
async def activate_task_discount(
    callback: CallbackQuery,
    callback_data: DiscountClick,
    session: AsyncSession,
    i18n: I18nContext,
) -> None:
    if not isinstance(callback.message, Message):
        await callback.answer()
        return

    user_id = callback.from_user.id
    task_id = callback_data.t_id
    discount = callback_data.dc

    user_repo = UserRepo(session)
    item_name = await user_repo.get_item_name_by_task_id(user_id, task_id, i18n.locale)

    await user_repo.activate_discount(user_id, task_id, discount)

    await callback.message.edit_text(
        text=f"{i18n.get("activate_discount-placeholder")}\n___"
        + "\n\n"
        + i18n.get(
            "activate_discount-activated", discount=discount, item_name=item_name
        ),
        reply_markup=inline.get_back_button(i18n),
    )
    await callback.answer()
