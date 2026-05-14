from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.utils.ui import render_item_card
from src.bot.keyboard import inline
from src.bot.keyboard.callback_data import DiscountOfferClick, ActivateDiscountClick
from src.db.repo import UserRepo

router = Router()


@router.callback_query(DiscountOfferClick.filter())
async def process_discount_selection(
    callback: CallbackQuery,
    callback_data: DiscountOfferClick,
    session: AsyncSession,
    i18n: I18nContext,
) -> None:
    task_id = callback_data.task_id
    discount = callback_data.discount

    repo = UserRepo(session)
    current_task = await repo.get_task_by_task_id(task_id)

    card_text, _, _ = await render_item_card(
        current_task.item_id, current_task.offer_idx, session, i18n, discount=discount
    )

    await callback.message.edit_text(  # type: ignore
        text=i18n.get("activate_discount-placeholder") + "\n\n" + card_text,
        reply_markup=inline.get_activate_discount_kb(
            task_id=task_id, discount=discount, i18n=i18n
        ),
    )
    await callback.answer()


@router.callback_query(ActivateDiscountClick.filter())
async def activate_task_discount(
    callback: CallbackQuery,
    callback_data: ActivateDiscountClick,
    session: AsyncSession,
    i18n: I18nContext,
) -> None:
    task_id = callback_data.task_id
    discount = callback_data.discount

    repo = UserRepo(session)
    item_name = await repo.get_item_name_by_task_id(task_id, i18n.locale)

    await repo.activate_discount(task_id, discount)

    await callback.message.edit_text(  # type: ignore
        text=i18n.get("activate_discount-placeholder")
        + "\n\n"
        + i18n.get(
            "activate_discount-activated", discount=discount, item_name=item_name
        ),
        reply_markup=inline.get_back_button(i18n),
    )
    await callback.answer()
