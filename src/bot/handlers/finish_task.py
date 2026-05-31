from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repo import UserRepo
from src.bot.keyboard import inline
from src.bot.keyboard.callback_data import FinishTaskClick

router = Router()


@router.callback_query(FinishTaskClick.filter())
async def finish_user_task(
    callback: CallbackQuery,
    callback_data: FinishTaskClick,
    session: AsyncSession,
    i18n: I18nContext,
) -> None:
    task_id = callback_data.task_id

    repo = UserRepo(session)
    await repo.drop_task(task_id)

    await callback.message.edit_text(  # type: ignore
        text=f"{i18n.get("finish_task-placeholder")}\n___"
        + "\n\n"
        + i18n.get("finish_task-finished"),
        reply_markup=inline.get_back_button(i18n),
    )
    await callback.answer()
