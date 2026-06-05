from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repo import UserRepo, ItemRepo
from src.bot.keyboard import inline
from src.bot.utils.states import AddTaskStates
from src.bot.keyboard.callback_data import AddTaskClick
from src.bot.keyboard.callback_data import AddTaskAction

from src.bot.utils.ui import render_item_card

router = Router()


@router.message(AddTaskStates.wait_for_item_name)
async def process_item_searching(
    message: Message, state: FSMContext, session: AsyncSession, i18n: I18nContext
) -> None:
    if not message.from_user:
        return

    repo = ItemRepo(session)
    items = await repo.search_items(str(message.text))

    if not items:
        await message.answer(
            text=f"{i18n.get("add_task-placeholder")}\n___"
            + "\n\n"
            + i18n.get("search-empty")
            + "\n"
            + i18n.get("enter-item-name-again"),
            reply_markup=inline.get_back_button(i18n),
        )
        return

    if len(items) == 1:
        target_item = items[0]

        text, kb, _ = await render_item_card(
            message.from_user.id,
            target_item.id,
            0,
            session,
            i18n,
        )
        await message.answer(
            text=f"{i18n.get("add_task-placeholder")}\n___" + "\n\n" + text,
            reply_markup=kb,
        )

        await state.clear()
        return

    await message.answer(
        text=f"{i18n.get("add_task-placeholder")}\n___"
        + "\n\n"
        + i18n.get("search-results"),
        reply_markup=inline.get_found_items_kb(items, i18n),
    )
    await state.clear()


@router.callback_query(AddTaskClick.filter(F.action == AddTaskAction.SEARCH))
async def process_item_selection(
    callback: CallbackQuery,
    callback_data: AddTaskClick,
    state: FSMContext,
    session: AsyncSession,
    i18n: I18nContext,
):
    if not isinstance(callback.message, Message):
        await callback.answer()
        return

    user_id = callback.from_user.id
    item_id = callback_data.item_id
    text, kb, _ = await render_item_card(user_id, item_id, 0, session, i18n)

    await callback.message.edit_text(
        text=f"{i18n.get("add_task-placeholder")}\n___" + "\n\n" + text,
        reply_markup=kb,
    )
    await state.clear()

    await callback.answer()


@router.callback_query(AddTaskClick.filter(F.action == AddTaskAction.NAVIGATION))
async def navigate_recipe(
    callback: CallbackQuery,
    callback_data: AddTaskClick,
    session: AsyncSession,
    i18n: I18nContext,
):
    if not isinstance(callback.message, Message):
        await callback.answer()
        return

    user_id = callback.from_user.id
    item_id = callback_data.item_id

    text, kb, _ = await render_item_card(
        user_id,
        item_id,
        int(callback_data.idx),
        session,
        i18n,
    )

    try:
        await callback.message.edit_text(
            text=f"{i18n.get("add_task-placeholder")}\n___" + "\n\n" + text,
            reply_markup=kb,
        )
    except Exception:
        pass

    await callback.answer()


@router.callback_query(AddTaskClick.filter(F.action == AddTaskAction.CONFIRM))
async def add_user_task(
    callback: CallbackQuery,
    callback_data: AddTaskClick,
    session: AsyncSession,
    i18n: I18nContext,
) -> None:
    if not isinstance(callback.message, Message):
        await callback.answer()
        return

    item_id = callback_data.item_id
    offer_idx = callback_data.offer_idx

    repo = UserRepo(session)
    is_task_exist = await repo.check_task_exists(callback.from_user.id, item_id)

    if is_task_exist:
        await callback.message.edit_text(
            text=f"{i18n.get("add_task-placeholder")}\n___"
            + "\n\n"
            + i18n.get("task-already-exist"),
            reply_markup=inline.get_back_button(i18n),
        )
        return

    await repo.add_task(
        user_id=callback.from_user.id, item_id=item_id, offer_idx=int(offer_idx)
    )

    await callback.message.edit_text(
        text=f"{i18n.get("add_task-placeholder")}\n___"
        + "\n\n"
        + i18n.get("add_task-created")
        + "\n"
        + i18n.get("add_task-good_luck"),
        reply_markup=inline.get_back_button(i18n),
    )
    await callback.answer()
