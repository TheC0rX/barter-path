from aiogram import Router
from aiogram.types import CallbackQuery, Message, InputRichMessage
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

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
    redis: Redis,
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

    current_task_idx = int(await redis.get(f"user:{user_id}:page") or 0)
    if current_task_idx == total_tasks - 1 and total_tasks > 1:
        current_task_idx = await redis.decr(f"user:{user_id}:page")

    await user_repo.complete_task(user_id, task_id)
    await callback.answer(
        text=i18n.get("finish_task-finished"),
        show_alert=False,
    )

    item_id = await user_repo.get_item_id_by_task_id(user_id, task_id)
    next_items = await item_repo.get_next_craft_items(item_id)

    if next_items:
        await callback.message.edit_text(
            rich_message=InputRichMessage(html=f"""
                    {i18n.get("finish_task-placeholder")}

                    {i18n.get("finish_task-next_tasks")}
                    {i18n.get("finish_task-next_tasks_list")}
                """),
            reply_markup=inline.get_found_items_kb(
                task_id,
                next_items,
                i18n,
                prev_id=item_id,
            ),
        )
    else:
        await show_main_menu(callback, session, i18n, redis)
