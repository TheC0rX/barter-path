from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repo import UserRepo
from src.bot.keyboards import inline
from src.bot.keyboards.callback_data import DeleteTaskClick

router = Router()


@router.callback_query(DeleteTaskClick.filter())
async def delete_user_task(
    callback: CallbackQuery,
    callback_data: DeleteTaskClick,
    session: AsyncSession,
    i18n: I18nContext,
) -> None:
    if not isinstance(callback.message, Message):
        await callback.answer()
        return

    user_id = callback.from_user.id
    task_id = callback_data.task_id

    repo = UserRepo(session)
    await repo.abandon_task(user_id, task_id)

    await callback.message.edit_text(
        text=f"{i18n.get("delete_task-placeholder")}\n___"
        + "\n\n"
        + i18n.get("delete_task-deleted"),
        reply_markup=inline.get_back_button(i18n),
    )
    await callback.answer()
