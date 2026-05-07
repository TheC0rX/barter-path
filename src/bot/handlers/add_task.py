from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repo import UserRepo, ItemRepo
from src.bot.keyboard import inline
from src.bot.utils.states import AddTaskStates
from src.bot.keyboard.callback_data import (
    RecipeNav,
    SearchItem,
    AddTaskClick,
)

from src.bot.utils.ui import render_item_card

router = Router()


@router.message(AddTaskStates.wait_for_item_name)
async def process_item_searching(
    message: Message, state: FSMContext, session: AsyncSession, i18n: I18nContext
) -> None:
    repo = ItemRepo(session)
    items = await repo.search_items(str(message.text))

    if not items:
        await message.answer(
            text=i18n.get("add_task-placeholder")
            + "\n\n"
            + i18n.get("search-empty")
            + "\n"
            + i18n.get("enter-item-name-again"),
            reply_markup=inline.get_back_button(i18n),
        )
        return

    if len(items) == 1:
        target_item = items[0]

        text, kb = await render_item_card(target_item.id, 0, session, i18n)
        await message.answer(
            text=i18n.get("add_task-placeholder") + "\n\n" + text, reply_markup=kb
        )

        await state.clear()
        return

    await message.answer(
        text=i18n.get("add_task-placeholder") + "\n\n" + i18n.get("search-results"),
        reply_markup=inline.get_found_items_kb(items, i18n),
    )


@router.callback_query(SearchItem.filter())
async def process_item_selection(
    callback: CallbackQuery,
    callback_data: SearchItem,
    state: FSMContext,
    session: AsyncSession,
    i18n: I18nContext,
):
    item_id = callback_data.item_id
    text, kb = await render_item_card(item_id, 0, session, i18n)

    await callback.message.edit_text(text=i18n.get("add_task-placeholder") + "\n\n" + text, reply_markup=kb)  # type: ignore
    await state.clear()

    await callback.answer()


@router.callback_query(RecipeNav.filter())
async def navigate_recipe(
    callback: CallbackQuery,
    callback_data: RecipeNav,
    session: AsyncSession,
    i18n: I18nContext,
):
    text, kb = await render_item_card(
        callback_data.item_id, int(callback_data.idx), session, i18n
    )

    try:
        await callback.message.edit_text(text=i18n.get("add_task-placeholder") + "\n\n" + text, reply_markup=kb)  # type: ignore
    except Exception:
        pass

    await callback.answer()


@router.callback_query(AddTaskClick.filter())
async def add_user_task(
    callback: CallbackQuery,
    callback_data: AddTaskClick,
    session: AsyncSession,
    i18n: I18nContext,
) -> None:
    item_id = callback_data.item_id
    offer_idx = callback_data.offer_idx

    repo = UserRepo(session)
    is_task_exist = await repo.check_task_exists(callback.from_user.id, item_id)

    if is_task_exist:
        await callback.message.edit_text(  # type: ignore
            text=i18n.get("add_task-placeholder")
            + "\n\n"
            + i18n.get("task-already-exist"),
            reply_markup=inline.get_back_button(i18n),
        )
        return

    await repo.add_task(
        user_id=callback.from_user.id, item_id=item_id, offer_idx=int(offer_idx)
    )

    await callback.message.edit_text(  # type: ignore
        text=i18n.get("add_task-placeholder")
        + "\n\n"
        + i18n.get("add_task-created")
        + "\n"
        + i18n.get("add_task-good_luck"),
        reply_markup=inline.get_back_button(i18n),
    )
    await callback.answer()
