from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repo import UserRepo
from src.bot.utils.ui import show_main_menu
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
    task_id = callback_data.t_id
    user_repo = UserRepo(session)

    tasks = await user_repo.get_user_tasks(user_id)
    total_tasks = len(tasks)

    target_idx = None
    for idx, task in enumerate(tasks):
        if task.id == task_id:
            target_idx = idx
            break

    if target_idx is not None:
        if target_idx == total_tasks - 1 and total_tasks > 1:
            task_idx = target_idx - 1
        else:
            task_idx = target_idx
    else:
        task_idx = 0

    await user_repo.abandon_task(user_id, task_id)
    await callback.answer(
        text=i18n.get("delete_task-deleted"),
        show_alert=False,
    )

    await show_main_menu(callback, session, i18n, task_idx=task_idx)
