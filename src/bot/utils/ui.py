from aiogram.types import CallbackQuery, Message
from aiogram_i18n import I18nContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repo import UserRepo, ItemRepo
from src.bot.keyboard import inline
from src.bot.keyboard.callback_data import RecipeNav, MenuClick, AddTaskClick


async def render_item_card(
    item_id: str, offer_idx: int, session: AsyncSession, i18n: I18nContext
):
    repo = ItemRepo(session)
    rows = await repo.get_item_recipes(item_id)

    offers_data = {}
    for recipe, ing_item in rows:
        ing_tuple = (ing_item, recipe.amount)

        if recipe.offer_index not in offers_data:
            offers_data[recipe.offer_index] = []

        if ing_tuple not in offers_data[recipe.offer_index]:
            offers_data[recipe.offer_index].append(ing_tuple)

    sorted_offer_indices = sorted(offers_data.keys())
    total_offers = len(sorted_offer_indices)

    if offer_idx >= total_offers:
        offer_idx = 0

    actual_offer_key = sorted_offer_indices[offer_idx]
    current_ings = offers_data[actual_offer_key]

    item = await repo.get_item(item_id)
    target_name = item.name_ru if i18n.locale == "ru" else item.name_en  # type: ignore

    text = f"{i18n.get("item_card-selected_item", item_name=target_name)}\n"
    text += f"{i18n.get('item_card-selected_offer', offer=offer_idx+1, total_offers=total_offers)}\n\n"
    text += f"{i18n.get('item_card-required_ings')}\n"

    for ing_item, amount in current_ings:
        name = ing_item.name_ru if i18n.locale == "ru" else ing_item.name_en
        text += f"- {name}: <code>{amount}</code> {i18n.get('item_card-pieces')}\n"

    builder = InlineKeyboardBuilder()

    if total_offers > 1:
        prev_idx = (offer_idx - 1) % total_offers
        next_idx = (offer_idx + 1) % total_offers
        builder.button(
            text="⬅️", callback_data=RecipeNav(item_id=item_id, idx=str(prev_idx))
        )
        builder.button(
            text="➡️", callback_data=RecipeNav(item_id=item_id, idx=str(next_idx))
        )

    builder.button(
        text=i18n.get("btn-confirm"),
        callback_data=AddTaskClick(item_id=item_id, offer_idx=offer_idx),
    )

    builder.button(
        text=i18n.get("btn-back"),
        callback_data=MenuClick(target="add_task"),
    )

    if total_offers > 1:
        builder.adjust(2, 1)
    else:
        builder.adjust(1)
    return text, builder.as_markup()


async def show_main_menu(
    event: Message | CallbackQuery,
    session: AsyncSession,
    i18n: I18nContext,
    task_idx: int = 0,
) -> None:
    repo = UserRepo(session)
    user_id = event.from_user.id  # type: ignore
    tasks = await repo.get_user_tasks(user_id)

    if not tasks:
        text = i18n.get("main_menu-placeholder") + "\n\n" + i18n.get("no-tasks")  # type: ignore
        kb = inline.get_main_menu_kb(i18n, has_tasks=False)
    else:
        current_task = tasks[task_idx % len(tasks)]
        card_text, _ = await render_item_card(
            current_task.item_id, current_task.offer_idx, session, i18n
        )

        text = i18n.get("main_menu-placeholder") + "\n\n" + card_text
        kb = inline.get_main_menu_kb(
            i18n,
            has_tasks=True,
            task_idx=task_idx,
            total_tasks=len(tasks),
            current_task_id=current_task.id,
        )

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text=text, reply_markup=kb)  # type: ignore
        await event.answer()
    else:
        await event.answer(text=text, reply_markup=kb)
