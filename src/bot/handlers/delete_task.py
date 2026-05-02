from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repo import UserRepo
from src.bot.keyboard import inline
from src.bot.keyboard.callback_data import (
    DeleteTaskClick,
    ConfirmDeleteClick,
    MenuClick,
)

router = Router()


@router.callback_query(DeleteTaskClick.filter())
async def process_task_confirmation(
    callback: CallbackQuery, callback_data: DeleteTaskClick, i18n: I18nContext
) -> None:
    task_id = callback_data.task_id

    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ " + i18n.get("buttons-confirm-yes"),
        callback_data=ConfirmDeleteClick(task_id=task_id),
    )
    builder.button(
        text="❌ " + i18n.get("buttons-confirm-no"),
        callback_data=MenuClick(target="main"),
    )
    builder.adjust(2)

    await callback.message.edit_text(  # type: ignore
        text=i18n.get("task-delete-confirm-text"), reply_markup=builder.as_markup()
    )
    await callback.answer()


@router.callback_query(ConfirmDeleteClick.filter())
async def delete_user_task(
    callback: CallbackQuery,
    callback_data: ConfirmDeleteClick,
    session: AsyncSession,
    i18n: I18nContext,
) -> None:
    task_id = callback_data.task_id

    repo = UserRepo(session)
    await repo.drop_task(task_id)

    await callback.message.edit_text(text=i18n.get("delete_task-deleted_success"), reply_markup=inline.get_back_button(i18n))  # type: ignore
    await callback.answer()
