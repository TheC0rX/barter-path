from aiogram.types import CallbackQuery, Message
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repo import UserRepo, ItemRepo
from src.bot.keyboard import inline


async def render_item_card(
    item_id: str,
    offer_idx: int,
    session: AsyncSession,
    i18n: I18nContext,
    discount: int = 0,
    task_id: int | None = None,
):
    repo = ItemRepo(session)
    user_repo = UserRepo(session)
    rows = await repo.get_item_recipes(item_id)

    progress_dict = {}
    if task_id:
        progress_dict = await user_repo.get_task_progress_dict(task_id)

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

    text = f"{item.icon if item is not None else ""} {i18n.get("item_card-selected_item", item_name=target_name)}\n"
    text += f"{get_nubmer_emoji(offer_idx+1)} {i18n.get('item_card-selected_offer', offer=offer_idx+1)}{f'/{total_offers}' if not task_id else ""}\n"
    if task_id:
        text += f"🎟️ {i18n.get("item_card-selected_discount", discount=discount)}\n"
    text += f"\n{i18n.get('item_card-required_ings')}\n"

    is_finished = True if task_id else False
    for ing_item, amount in current_ings:
        name = ing_item.name_ru if i18n.locale == "ru" else ing_item.name_en
        discount_amount = max(1, round(amount * (1 - discount / 100)))

        if task_id:
            collected = progress_dict.get(ing_item.id, 0)
            remains = max(0, discount_amount - collected)

            if remains == 0:
                status = "✅"
            else:
                status = "⌛"
                is_finished = False

            text += f"{status} {name}: <code>{collected}</code>/<code>{discount_amount}</code>\n"
            if remains > 0:
                text += f"└ {i18n.get("item_card-remains", amount=remains)}\n"

        else:
            if amount != discount_amount:
                text += f"- {name}: <s>{amount}</s> <code>{discount_amount}</code> {i18n.get('item_card-pieces')}\n"
            else:
                text += (
                    f"- {name}: <code>{amount}</code> {i18n.get('item_card-pieces')}\n"
                )

    if task_id:
        return text, None, is_finished

    kb = inline.get_card_nav_kb(offer_idx, total_offers, item_id, i18n)
    return text, kb, False


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
        card_text, _, is_finished = await render_item_card(
            current_task.item_id,
            current_task.offer_idx,
            session,
            i18n,
            discount=current_task.discount,
            task_id=current_task.id,
        )

        text = (
            i18n.get("main_menu-placeholder")
            + "\n\n"
            + i18n.get(
                "main_menu-pagination",
                current_task=(task_idx % len(tasks)) + 1,
                total_tasks=len(tasks),
            )
            + "\n\n"
            + card_text
        )
        kb = inline.get_main_menu_kb(
            i18n,
            has_tasks=True,
            task_idx=task_idx,
            total_tasks=len(tasks),
            current_task_id=current_task.id,
            is_finished=is_finished,
        )

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text=text, reply_markup=kb)  # type: ignore
        await event.answer()
    else:
        await event.answer(text=text, reply_markup=kb)


def get_nubmer_emoji(number: int) -> str:
    emoji_numbers = {
        0: "0️⃣",
        1: "1️⃣",
        2: "2️⃣",
        3: "3️⃣",
        4: "4️⃣",
        5: "5️⃣",
        6: "6️⃣",
        7: "7️⃣",
        8: "8️⃣",
        9: "9️⃣",
    }

    return "".join(emoji_numbers[int(char)] for char in str(number))
