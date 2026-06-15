from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repo import UserRepo, ItemRepo
from src.bot.keyboards import inline
from src.bot.utils.states import AddTaskStates
from src.bot.keyboards.callback_data import AddTaskClick
from src.bot.keyboards.callback_data import AddTaskAction

from src.bot.utils.ui import render_item_card, show_main_menu

router = Router()


@router.message(AddTaskStates.wait_for_item_name)
async def process_item_searching(
    message: Message, state: FSMContext, session: AsyncSession, i18n: I18nContext
) -> None:
    if not message.from_user:
        return

    data = await state.get_data()
    task_id = data.get("task_id", 0)

    repo = ItemRepo(session)
    items = await repo.search_items(str(message.text))

    if not items:
        await message.answer(
            text=f"{i18n.get("add_task-placeholder")}\n___"
            + "\n\n"
            + i18n.get("search-empty")
            + "\n"
            + i18n.get("enter-item-name-again"),
            reply_markup=inline.get_back_button(task_id, i18n),
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
            task_id=task_id,
            is_preview=True,
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
        reply_markup=inline.get_found_items_kb(task_id, items, i18n),
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
    task_id = callback_data.t_id
    task_idx = callback_data.t_idx

    text, kb, _ = await render_item_card(
        user_id,
        item_id,
        0,
        session,
        i18n,
        prev_id=callback_data.prev_id,
        task_id=task_id,
        task_idx=task_idx,
        is_preview=True,
    )

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
    task_id = callback_data.t_id
    task_idx = callback_data.t_idx

    text, kb, _ = await render_item_card(
        user_id,
        item_id,
        int(callback_data.idx),
        session,
        i18n,
        prev_id=callback_data.prev_id,
        task_id=task_id,
        task_idx=task_idx,
        is_preview=True,
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

    user_id = callback.from_user.id
    task_id = callback_data.t_id
    item_id = callback_data.item_id
    offer_idx = callback_data.o_idx
    prev_id = callback_data.prev_id
    task_idx = callback_data.t_idx

    repo = UserRepo(session)
    is_task_exist = await repo.check_task_exists(user_id, item_id)

    if is_task_exist:
        await callback.message.edit_text(
            text=f"{i18n.get("add_task-placeholder")}\n___"
            + "\n\n"
            + i18n.get("task-already-exist"),
            reply_markup=inline.get_back_button(task_id, i18n, task_idx=task_idx),
        )
        return

    new_task = await repo.add_task(
        user_id=user_id, item_id=item_id, offer_idx=int(offer_idx)
    )
    new_task_id = new_task.id
    if prev_id:
        await repo.add_resource_amount(
            user_id,
            new_task_id,
            prev_id,
            delta_value=1,
        )

    await callback.answer(
        text=f"{i18n.get("add_task-created")}\n{i18n.get("add_task-good_luck")}",
        show_alert=False,
    )

    await show_main_menu(callback, session, i18n, task_idx=-1)
