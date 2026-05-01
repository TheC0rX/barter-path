from aiogram import Router
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repo import ItemRepo
from src.bot.utils.states import AddTaskStates
from src.bot.keyboard.callback_data import MenuClick

router = Router()


@router.message(AddTaskStates.wait_for_item_name)
async def search_item(
    message: Message, session: AsyncSession, i18n: I18nContext
) -> None:
    repo = ItemRepo(session)
    items = await repo.search_items(str(message.text))

    if not items:
        await message.answer(i18n.get("add_item-search_empty"))
        return

    builder = InlineKeyboardBuilder()
    for item in items:
        display_name = item.name_ru if i18n.locale == "ru" else item.name_en
        builder.button(text=display_name, callback_data=f"select_task_item:{item.id}")
    builder.button(
        text="⬅️ " + i18n.get("buttons-back"), callback_data=MenuClick(target="main")
    )
    builder.adjust(1)

    await message.answer(
        text=i18n.get("add_task-search_results"), reply_markup=builder.as_markup()
    )
