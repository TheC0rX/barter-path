from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repo import UserRepo
from src.bot.keyboard import inline
from src.bot.keyboard.callback_data import (
    DeleteTaskClick,
    ConfirmDeleteTaskClick,
    MenuClick,
)

router = Router()


@router.callback_query(DeleteTaskClick.filter())
async def process_delete_task_confirmation(
    callback: CallbackQuery,
    callback_data: DeleteTaskClick,
    session: AsyncSession,
    i18n: I18nContext,
) -> None:
    task_id = callback_data.task_id

    repo = UserRepo(session)
    item_name = await repo.get_item_name_by_task_id(task_id=task_id, locale=i18n.locale)

    builder = InlineKeyboardBuilder()
    builder.button(
        text=i18n.get("btn-confirm"),
        callback_data=ConfirmDeleteTaskClick(task_id=task_id),
    )
    builder.button(
        text=i18n.get("btn-cancel"),
        callback_data=MenuClick(target="main"),
    )
    builder.adjust(2)

    await callback.message.edit_text(  # type: ignore
        text=i18n.get("delete_task-placeholder")
        + "\n\n"
        + i18n.get("delete_task-confirmation", item_name=item_name),
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(ConfirmDeleteTaskClick.filter())
async def delete_user_task(
    callback: CallbackQuery,
    callback_data: ConfirmDeleteTaskClick,
    session: AsyncSession,
    i18n: I18nContext,
) -> None:
    task_id = callback_data.task_id

    repo = UserRepo(session)
    await repo.drop_task(task_id)

    await callback.message.edit_text(  # type: ignore
        text=i18n.get("delete_task-placeholder")
        + "\n\n"
        + i18n.get("delete_task-deleted"),
        reply_markup=inline.get_back_button(i18n),
    )
    await callback.answer()
