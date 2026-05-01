from aiogram import Router, F
from aiogram.types.callback_query import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.keyboard import inline
from src.bot.keyboard.callback_data import MenuClick
from src.bot.utils.states import AddTaskStates
from src.db.repo import UserRepo

router = Router()


@router.callback_query(MenuClick.filter(F.target == "main"))
async def open_main_menu(
    callback: CallbackQuery, state: FSMContext, i18n: I18nContext
) -> None:
    if state.get_state:
        await state.clear()

    await callback.message.edit_text(  # type: ignore
        text=i18n.get("menu-main-text", name=callback.from_user.first_name),
        reply_markup=inline.get_main_menu_kb(i18n),
    )
    await callback.answer()


@router.callback_query(MenuClick.filter(F.target == "add_task"))
async def open_add_task(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, i18n: I18nContext
) -> None:
    repo = UserRepo(session)
    user_tasks_count = await repo.get_user_tasks_count(callback.from_user.id)

    if user_tasks_count >= 3:
        await callback.message.edit_text(text=i18n.get("too-many-tasks"), reply_markup=inline.get_back_button(i18n))  # type: ignore
        return

    await state.set_state(AddTaskStates.wait_for_item_name)
    await callback.message.edit_text(  # type: ignore
        text=i18n.get("menu-add_task-text"),
        reply_markup=inline.get_back_button(i18n),
    )
    await callback.answer()


@router.callback_query(MenuClick.filter(F.target == "settings"))
async def open_settings(callback: CallbackQuery, i18n: I18nContext) -> None:
    await callback.message.edit_text(  # type: ignore
        text=i18n.get("menu-settings-text"),
        reply_markup=inline.get_settings_kb(i18n),
    )
    await callback.answer()
