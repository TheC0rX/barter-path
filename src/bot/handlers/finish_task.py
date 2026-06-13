from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repo import UserRepo, ItemRepo
from src.bot.utils.ui import show_main_menu
from src.bot.keyboards import inline
from src.bot.keyboards.callback_data import FinishTaskClick

router = Router()


@router.callback_query(FinishTaskClick.filter())
async def finish_user_task(
    callback: CallbackQuery,
    callback_data: FinishTaskClick,
    session: AsyncSession,
    i18n: I18nContext,
) -> None:
    if not isinstance(callback.message, Message):
        await callback.answer()
        return

    user_id = callback.from_user.id
    task_id = callback_data.t_id

    user_repo = UserRepo(session)
    item_repo = ItemRepo(session)

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

    await user_repo.complete_task(user_id, task_id)
    await callback.answer(
        text=i18n.get("finish_task-finished"),
        show_alert=False,
    )

    current_task = await user_repo.get_task_by_task_id(user_id, task_id)
    next_items = await item_repo.get_next_craft_items(current_task.item_id)

    if next_items:
        await callback.message.edit_text(
            text=f"{i18n.get("finish_task-placeholder")}\n___"
            + "\n\n"
            + f"{i18n.get("finish_task-next_tasks")}\n{i18n.get("finish_task-next_tasks_list")}",
            reply_markup=inline.get_found_items_kb(
                task_id,
                next_items,
                i18n,
                prev_id=current_task.item_id,
                task_idx=task_idx,
            ),
        )
    else:
        await show_main_menu(callback, session, i18n, task_idx=task_idx)
