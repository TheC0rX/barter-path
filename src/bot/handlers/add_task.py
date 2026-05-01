from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repo import ItemRepo
from src.bot.utils.states import AddTaskStates
from src.bot.keyboard.callback_data import MenuClick, RecipeNav

from src.bot.utils.render import render_item_card

router = Router()


@router.message(AddTaskStates.wait_for_item_name)
async def search_item(
    message: Message, state: FSMContext, session: AsyncSession, i18n: I18nContext
) -> None:
    repo = ItemRepo(session)
    items = await repo.search_items(str(message.text))

    if not items:
        await message.answer(i18n.get("add_item-search_empty"))
        return

    if len(items) == 1:
        target_item = items[0]

        text, kb = await render_item_card(target_item.id, 0, session, i18n)
        await message.answer(text=text, reply_markup=kb)

        await state.clear()
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


@router.callback_query(
    AddTaskStates.wait_for_item_name, F.data.startswith("select_task_item:")
)
async def process_item_selection(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, i18n: I18nContext
):
    item_id = str(callback.data).split(":")[1]
    text, kb = await render_item_card(item_id, 0, session, i18n)

    await callback.message.edit_text(text=text, reply_markup=kb)  # type: ignore
    await state.clear()
    await callback.answer()


@router.callback_query(RecipeNav.filter())
async def navigate_recipe(
    callback: CallbackQuery,
    callback_data: RecipeNav,
    session: AsyncSession,
    i18n: I18nContext,
):
    text, kb = await render_item_card(
        callback_data.item_id, int(callback_data.idx), session, i18n
    )

    try:
        await callback.message.edit_text(text=text, reply_markup=kb)  # type: ignore
    except Exception:
        pass

    await callback.answer()
