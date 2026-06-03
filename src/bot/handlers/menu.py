from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.keyboard import inline
from src.bot.keyboard.callback_data import MenuClick, MenuNav
from src.bot.keyboard.callback_data import MenuAction
from src.bot.utils.ui import show_main_menu
from src.bot.utils.states import AddTaskStates
from src.db.repo import UserRepo, ItemRepo

router = Router()


@router.callback_query(MenuNav.filter())
async def navigate_menu_tasks(
    callback: CallbackQuery,
    callback_data: MenuNav,
    session: AsyncSession,
    i18n: I18nContext,
):
    await show_main_menu(callback, session, i18n, task_idx=callback_data.task_index)


@router.callback_query(MenuClick.filter(F.target == MenuAction.MENU))
async def open_main_menu(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, i18n: I18nContext
) -> None:
    await state.clear()

    await show_main_menu(callback, session, i18n)


@router.callback_query(MenuClick.filter(F.target == MenuAction.FINISH_TASK))
async def open_finish_task(
    callback: CallbackQuery,
    callback_data: MenuClick,
    session: AsyncSession,
    i18n: I18nContext,
) -> None:
    if not isinstance(callback.message, Message):
        await callback.answer()
        return

    task_id = callback_data.task_id

    repo = UserRepo(session)
    item_name = await repo.get_item_name_by_task_id(task_id=task_id, locale=i18n.locale)

    await callback.message.edit_text(
        text=f"{i18n.get("finish_task-placeholder")}\n___"
        + "\n\n"
        + i18n.get("finish_task-confirmation", item_name=item_name),
        reply_markup=inline.get_finish_task_kb(task_id=task_id, i18n=i18n),
    )
    await callback.answer()


@router.callback_query(MenuClick.filter(F.target == MenuAction.ADD_TASK))
async def open_add_task(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, i18n: I18nContext
) -> None:
    if not isinstance(callback.message, Message):
        await callback.answer()
        return

    repo = UserRepo(session)
    user_tasks_count = await repo.get_user_tasks_count(callback.from_user.id)

    if user_tasks_count >= 3:
        await callback.message.edit_text(
            text=f"{i18n.get("main_menu-placeholder")}\n___"
            + "\n\n"
            + i18n.get("too-many-tasks"),
            reply_markup=inline.get_back_button(i18n),
        )
        return

    await state.set_state(AddTaskStates.wait_for_item_name)
    await callback.message.edit_text(
        text=f"{i18n.get("add_task-placeholder")}\n___"
        + "\n\n"
        + i18n.get("enter-item-name"),
        reply_markup=inline.get_back_button(i18n),
    )
    await callback.answer()


@router.callback_query(MenuClick.filter(F.target == MenuAction.DELETE_TASK))
async def open_delete_task(
    callback: CallbackQuery,
    callback_data: MenuClick,
    session: AsyncSession,
    i18n: I18nContext,
) -> None:
    if not isinstance(callback.message, Message):
        await callback.answer()
        return

    task_id = callback_data.task_id

    repo = UserRepo(session)
    item_name = await repo.get_item_name_by_task_id(task_id=task_id, locale=i18n.locale)

    await callback.message.edit_text(
        text=f"{i18n.get("delete_task-placeholder")}\n___"
        + "\n\n"
        + i18n.get("delete_task-confirmation", item_name=item_name),
        reply_markup=inline.get_delete_task_kb(task_id=task_id, i18n=i18n),
    )
    await callback.answer()


@router.callback_query(MenuClick.filter(F.target == MenuAction.ACTIVATE_DISCOUNT))
async def open_activate_discount(
    callback: CallbackQuery, callback_data: MenuClick, i18n: I18nContext
) -> None:
    if not isinstance(callback.message, Message):
        await callback.answer()
        return

    task_id = callback_data.task_id

    await callback.message.edit_text(
        text=f"{i18n.get("activate_discount-placeholder")}\n___"
        + "\n\n"
        + i18n.get("select-discount"),
        reply_markup=inline.get_discount_offers_kb(task_id, i18n),
    )
    await callback.answer()


@router.callback_query(MenuClick.filter(F.target == MenuAction.MANAGE_RESOURCES))
async def open_manage_resources(
    callback: CallbackQuery,
    callback_data: MenuClick,
    session: AsyncSession,
    i18n: I18nContext,
) -> None:
    if not isinstance(callback.message, Message):
        await callback.answer()
        return

    task_id = callback_data.task_id

    user_repo = UserRepo(session)
    item_repo = ItemRepo(session)

    task = await user_repo.get_task_by_task_id(task_id)
    rows = await item_repo.get_item_recipes(task.item_id)
    progress_dict = await user_repo.get_task_progress_dict(task_id)

    current_ings = [
        (ing_item, recipe.amount)
        for recipe, ing_item in rows
        if recipe.offer_index == task.offer_idx
    ]

    await callback.message.edit_text(
        text=f"{i18n.get("manage_resources-placeholder")}\n___"
        + "\n\n"
        + i18n.get("select-ingredient"),
        reply_markup=inline.get_resources_management_kb(
            task_id=task_id,
            current_ings=current_ings,
            progress_dict=progress_dict,
            discount=task.discount,
            i18n=i18n,
        ),
    )
    await callback.answer()


@router.callback_query(MenuClick.filter(F.target == MenuAction.SETTINGS))
async def open_settings(callback: CallbackQuery, i18n: I18nContext) -> None:
    if not isinstance(callback.message, Message):
        await callback.answer()
        return

    await callback.message.edit_text(
        text=f"{i18n.get("settings-placeholder")}\n___"
        + "\n\n"
        + i18n.get("settings-description-text"),
        reply_markup=inline.get_settings_kb(i18n),
    )
    await callback.answer()
