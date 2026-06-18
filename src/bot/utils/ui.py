from aiogram.types import CallbackQuery, Message, InputRichMessage
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repo import UserRepo, ItemRepo
from src.bot.keyboards import inline


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


async def render_item_card(
    user_id: int,
    item_id: str,
    offer_idx: int,
    session: AsyncSession,
    i18n: I18nContext,
    discount: int = 0,
    task_id: int | None = None,
    prev_id: str = "",
    task_idx: int | None = None,
    is_preview: bool = False,
):
    item_repo = ItemRepo(session)
    user_repo = UserRepo(session)

    offers_data = await item_repo.get_grouped_offers(item_id)
    sorted_offer_indices = sorted(offers_data.keys())
    total_offers = len(sorted_offer_indices)

    if offer_idx >= total_offers:
        offer_idx = 0

    actual_offer_key = sorted_offer_indices[offer_idx]
    current_ings = offers_data[actual_offer_key]

    item = await item_repo.get_item(item_id)
    target_name = item.name_ru if i18n.locale == "ru" else item.name_en
    offer_icon = get_nubmer_emoji(offer_idx + 1)

    offer_suffix = "" if task_id else f"/{total_offers}"
    text_lines = [
        f"{i18n.get("item_card-selected_item", icon=item.icon, item_name=target_name)}",
        f"{i18n.get('item_card-selected_offer', icon=offer_icon, offer=offer_idx+1, total_offers=offer_suffix)}",
    ]

    if task_id:
        text_lines.append(
            f"{i18n.get("item_card-selected_discount", discount=discount)}"
        )

    text_lines.append(f"{i18n.get('item_card-required_ings')}")

    is_finished = bool(task_id) and not is_preview
    progress_dict = (
        await user_repo.get_task_progress_dict(user_id, task_id)
        if task_id and not is_preview
        else {}
    )

    for ing_item, amount in current_ings:
        is_money = ing_item.id == "money"
        min_amount = 0 if is_money else 1
        discount_amount = max(min_amount, round(amount * (1 - discount / 100)))
        name = ing_item.name_ru if i18n.locale == "ru" else ing_item.name_en
        unit = "₽" if is_money else i18n.get("item_card-pieces", amount=discount_amount)

        if task_id and not is_preview:
            collected = progress_dict.get(ing_item.id, 0)
            remains = max(0, discount_amount - collected)
            display_collected = min(collected, discount_amount)

            if remains == 0:
                icon = "✅"
            else:
                icon = "💵" if is_money else "⌛"
                is_finished = False

            text_lines.append(
                i18n.get(
                    "ing_format-main_menu",
                    icon=icon,
                    item=name,
                    collected_amount=display_collected,
                    required_amount=discount_amount,
                    unit=unit,
                )
            )
            if remains > 0:
                text_lines.append(f"{i18n.get("item_card-remains", amount=remains)}")

        else:
            if amount != discount_amount:
                text_lines.append(
                    i18n.get(
                        "ing_format-discount_menu",
                        item=name,
                        amount=amount,
                        discount_amount=discount_amount,
                        unit=unit,
                    )
                )
            else:
                text_lines.append(
                    i18n.get(
                        "ing_format-resource_amount",
                        item=name,
                        amount=amount,
                        unit=unit,
                    )
                )

    text = "".join(text_lines)

    kb = inline.get_card_nav_kb(
        task_id if task_id else 0,
        offer_idx,
        total_offers,
        item_id,
        i18n,
        prev_id=prev_id,
        task_idx=task_idx,
    )
    return text, kb, is_finished if task_id and not is_preview else False


async def show_main_menu(
    event: Message | CallbackQuery,
    session: AsyncSession,
    i18n: I18nContext,
    task_idx: int | None = None,
    task_id: int | None = None,
) -> None:
    if not event.from_user:
        return

    user_repo = UserRepo(session)
    user_id = event.from_user.id
    tasks = await user_repo.get_user_tasks(user_id)

    if not tasks:
        text = f"""
            {i18n.get("main_menu-placeholder")}

            {i18n.get("no-tasks")}
        """
        kb = inline.get_main_menu_kb(i18n, has_tasks=False)

    else:
        if task_id is not None:
            current_task_idx = 0
            for idx, task in enumerate(tasks):
                if task.id == task_id:
                    current_task_idx = idx
                    break
        elif task_idx is not None:
            current_task_idx = task_idx % len(tasks)
        else:
            current_task_idx = 0

        current_task = tasks[current_task_idx]
        card_text, _, is_finished = await render_item_card(
            user_id,
            current_task.item_id,
            current_task.offer_idx,
            session,
            i18n,
            current_task.discount,
            current_task.id,
        )

        text = f"""
            {i18n.get("main_menu-placeholder")}
            
            {card_text}
        """
        kb = inline.get_main_menu_kb(
            i18n=i18n,
            has_tasks=True,
            task_idx=current_task_idx,
            total_tasks=len(tasks),
            current_task_id=current_task.id,
            is_finished=is_finished,
        )

    if isinstance(event, CallbackQuery):
        if not isinstance(event.message, Message):
            await event.answer()
            return

        await event.message.edit_text(
            rich_message=InputRichMessage(html=text),
            reply_markup=kb,
        )
        await event.answer()
    else:
        await event.answer_rich(
            rich_message=InputRichMessage(html=text),
            reply_markup=kb,
        )
