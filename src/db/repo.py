from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func, delete, update
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.dialects.postgresql import insert

from src.db.models import TaskStatus
from src.db.models import (
    User,
    Item,
    Recipe,
    UserTask,
    TaskProgress,
    ResourceLog,
    ResourceActionType,
    StalcraftVersion,
)


class UserRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_task_index(self, user_id: int, task_id: int) -> int:
        tasks = await self.get_user_tasks(user_id)

        for idx, task in enumerate(tasks):
            if task.id == task_id:
                return idx
        return 0

    async def add_user(self, user_id: int, locale: str) -> None:
        stmt = (
            insert(User)
            .values(user_id=user_id, locale=locale)
            .on_conflict_do_nothing(index_elements=[User.user_id])
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_user_locale(self, user_id: int) -> str | None:
        stmt = select(User.locale).where(User.user_id == user_id)

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_user_locale(self, user_id: int, locale: str) -> None:
        stmt = update(User).where(User.user_id == user_id).values(locale=locale)
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_user_tasks_count(self, user_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(UserTask)
            .where(
                UserTask.user_id == user_id,
                UserTask.status == TaskStatus.IN_PROGRESS,
            )
        )
        result = await self.session.execute(stmt)

        return result.scalar() or 0

    async def check_task_exists(self, user_id: int, item_id: str) -> bool:
        stmt = select(UserTask).where(
            UserTask.user_id == user_id,
            UserTask.item_id == item_id,
            UserTask.status == TaskStatus.IN_PROGRESS,
        )
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none() is not None

    async def has_tasks(self, user_id: int) -> bool:
        stmt = (
            select(UserTask)
            .where(
                UserTask.user_id == user_id,
                UserTask.status == TaskStatus.IN_PROGRESS,
            )
            .limit(1)
        )
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none() is not None

    async def get_user_tasks(self, user_id: int):
        stmt = (
            select(UserTask)
            .options(
                joinedload(UserTask.item),
                selectinload(UserTask.progress).joinedload(
                    TaskProgress.ingredient_item
                ),
            )
            .where(
                UserTask.user_id == user_id,
                UserTask.status == TaskStatus.IN_PROGRESS,
            )
            .order_by(UserTask.id.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add_task(self, user_id: int, item_id: str, offer_idx: int) -> UserTask:
        new_task = UserTask(user_id=user_id, item_id=item_id, offer_idx=offer_idx)
        self.session.add(new_task)
        await self.session.flush()

        recipe_stmt = (
            select(Recipe)
            .where(Recipe.item_id == item_id, Recipe.offer_index == offer_idx)
            .order_by(Recipe.ingredient_index.asc())
        )
        recipe_result = await self.session.execute(recipe_stmt)
        ingredients = recipe_result.scalars().all()

        for ingredient in ingredients:
            progress = TaskProgress(
                task_id=new_task.id,
                ingredient_id=ingredient.ingredient_id,
                collected_amount=0,
            )
            self.session.add(progress)

        await self.session.commit()

        return new_task

    async def complete_task(self, user_id: int, task_id: int) -> None:
        stmt = (
            select(Recipe.ingredient_id, Recipe.amount, UserTask.discount)
            .join(UserTask, UserTask.item_id == Recipe.item_id)
            .where(
                UserTask.id == task_id,
                UserTask.user_id == user_id,
                UserTask.status == TaskStatus.IN_PROGRESS,
                Recipe.offer_index == UserTask.offer_idx,
            )
            .with_for_update(of=UserTask)
        )
        result = await self.session.execute(stmt)
        rows = result.all()

        if not rows:
            return

        resources_dict = {}
        task_discount = rows[0][2]

        for ing_id, recipe_amount, _ in rows:
            min_amount = 0 if ing_id == "money" else 1

            final_amount = max(
                min_amount, round(recipe_amount * (1 - task_discount / 100))
            )
            resources_dict[ing_id] = final_amount

        snapshot_data = {
            "resources": resources_dict,
        }

        update_stmt = (
            update(UserTask)
            .where(UserTask.id == task_id)
            .values(
                status=TaskStatus.COMPLETED,
                finished_at=datetime.now(timezone.utc),
                craft_snapshot=snapshot_data,
            )
        )
        await self.session.execute(update_stmt)

        progress_stmt = delete(TaskProgress).where(TaskProgress.task_id == task_id)
        await self.session.execute(progress_stmt)

        await self.session.commit()

    async def abandon_task(self, user_id: int, task_id: int):
        check_stmt = select(UserTask.id).where(
            UserTask.id == task_id,
            UserTask.user_id == user_id,
            UserTask.status == TaskStatus.IN_PROGRESS,
        )
        check_result = await self.session.execute(check_stmt)
        rows = check_result.scalar_one_or_none()

        if not rows:
            return

        stmt = (
            update(UserTask)
            .where(UserTask.id == task_id)
            .values(
                status=TaskStatus.ABANDONED,
                finished_at=datetime.now(timezone.utc),
            )
        )
        await self.session.execute(stmt)

        progress_stmt = delete(TaskProgress).where(TaskProgress.task_id == task_id)
        await self.session.execute(progress_stmt)

        await self.session.commit()

    async def activate_discount(self, user_id: int, task_id: int, discount: int):
        stmt = (
            update(UserTask)
            .where(
                UserTask.id == task_id,
                UserTask.user_id == user_id,
            )
            .values(discount=discount)
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_task_by_task_id(self, user_id: int, task_id: int) -> UserTask:
        stmt = (
            select(UserTask)
            .options(joinedload(UserTask.item))
            .where(
                UserTask.id == task_id,
                UserTask.user_id == user_id,
            )
        )
        result = await self.session.execute(stmt)

        return result.scalar_one()

    async def get_item_name_by_task_id(
        self, user_id: int, task_id: int, locale: str
    ) -> str:
        name_col = Item.name_ru if locale == "ru" else Item.name_en
        stmt = (
            select(name_col)
            .join(UserTask, UserTask.item_id == Item.id)
            .where(
                UserTask.id == task_id,
                UserTask.user_id == user_id,
            )
        )

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_task_progress_dict(
        self,
        user_id: int,
        task_id: int,
    ) -> dict[str, int]:
        stmt = (
            select(TaskProgress.ingredient_id, TaskProgress.collected_amount)
            .join(UserTask, TaskProgress.task_id == UserTask.id)
            .where(
                TaskProgress.task_id == task_id,
                UserTask.user_id == user_id,
            )
            .order_by(TaskProgress.id.asc())
        )
        result = await self.session.execute(stmt)
        return dict(result.tuples().all())

    async def add_resource_amount(
        self, user_id: int, task_id: int, ing_id: str, delta_value: int
    ) -> None:
        stmt = (
            select(TaskProgress.collected_amount)
            .join(UserTask, TaskProgress.task_id == UserTask.id)
            .where(
                UserTask.id == task_id,
                UserTask.user_id == user_id,
                TaskProgress.ingredient_id == ing_id,
            )
            .with_for_update()
        )
        res = await self.session.execute(stmt)
        old_amount = res.scalar_one()
        new_amount = old_amount + delta_value

        update_stmt = (
            update(TaskProgress)
            .where(
                TaskProgress.task_id == task_id, TaskProgress.ingredient_id == ing_id
            )
            .values(collected_amount=new_amount)
        )
        await self.session.execute(update_stmt)

        log_entry = ResourceLog(
            user_id=user_id,
            task_id=task_id,
            ingredient_id=ing_id,
            action_type=ResourceActionType.ADD,
            delta_value=delta_value,
            old_amount=old_amount,
            new_amount=new_amount,
        )
        self.session.add(log_entry)
        await self.session.commit()

    async def reset_resource_amount(
        self, user_id: int, task_id: int, ing_id: str
    ) -> None:
        stmt = (
            select(TaskProgress.collected_amount)
            .join(UserTask, TaskProgress.task_id == UserTask.id)
            .where(
                UserTask.id == task_id,
                UserTask.user_id == user_id,
                TaskProgress.ingredient_id == ing_id,
            )
            .with_for_update()
        )
        res = await self.session.execute(stmt)
        old_amount = res.scalar_one()

        update_stmt = (
            update(TaskProgress)
            .where(
                TaskProgress.task_id == task_id, TaskProgress.ingredient_id == ing_id
            )
            .values(collected_amount=0)
        )
        await self.session.execute(update_stmt)

        log_entry = ResourceLog(
            user_id=user_id,
            task_id=task_id,
            ingredient_id=ing_id,
            action_type=ResourceActionType.RESET,
            delta_value=0,
            old_amount=old_amount,
            new_amount=0,
        )
        self.session.add(log_entry)
        await self.session.commit()

    async def get_resource_stats(
        self, user_id: int, task_id: int, ing_id: str
    ) -> tuple[int, int]:
        stmt = (
            select(UserTask.discount, Recipe.amount, TaskProgress.collected_amount)
            .join(Recipe, Recipe.item_id == UserTask.item_id)
            .join(
                TaskProgress,
                (TaskProgress.task_id == UserTask.id)
                & (TaskProgress.ingredient_id == Recipe.ingredient_id),
            )
            .where(
                UserTask.id == task_id,
                UserTask.user_id == user_id,
                Recipe.ingredient_id == ing_id,
                Recipe.offer_index == UserTask.offer_idx,
            )
        )

        result = await self.session.execute(stmt)
        row = result.tuples().first()

        if not row:
            return 0, 0

        discount, recipe_amount, collected_amount = row
        min_amount = 0 if ing_id == "money" else 1

        discount_amount = max(min_amount, round(recipe_amount * (1 - discount / 100)))
        display_collected = min(collected_amount, discount_amount)

        return display_collected, discount_amount


class ItemRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def search_items(self, query: str):
        clean_query = query.strip().lower()
        for char in "«»\"'.-":
            clean_query = clean_query.replace(char, " ")

        search_pattern = f"%{'%'.join(clean_query.split())}%"

        stmt = (
            select(Item)
            .where(
                Item.is_barterable == True,
                or_(
                    Item.name_ru.ilike(search_pattern),
                    Item.name_en.ilike(search_pattern),
                ),
            )
            .limit(5)
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_item_recipes(self, item_id: str):
        stmt = (
            select(Recipe, Item)
            .join(Item, Recipe.ingredient_id == Item.id)
            .where(Recipe.item_id == item_id)
            .order_by(Recipe.offer_index.asc(), Recipe.ingredient_index.asc())
        )

        result = await self.session.execute(stmt)
        return result.all()

    async def get_item(self, item_id: str) -> Item:
        stmt = select(Item).where(Item.id == item_id)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_grouped_offers(
        self, item_id: str
    ) -> dict[int, list[tuple[Item, int]]]:
        rows = await self.get_item_recipes(item_id)
        offers_data = {}

        for recipe, ing_item in rows:
            ing_tuple = (ing_item, recipe.amount)
            offers_data.setdefault(recipe.offer_index, [])

            if ing_tuple not in offers_data[recipe.offer_index]:
                offers_data[recipe.offer_index].append(ing_tuple)

        return offers_data

    async def get_next_craft_items(self, item_id: str) -> list[Item]:
        stmt = (
            select(Item)
            .join(Recipe, Recipe.item_id == Item.id)
            .where(Recipe.ingredient_id == item_id)
            .options(selectinload(Item.recipe_results))
            .distinct()
            .limit(5)
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class StalcraftRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def update_items_and_recipes(
        self, items_data: list[dict], recipes_list: list[Recipe]
    ):
        await self.session.execute(delete(Recipe))

        if items_data:
            stmt = insert(Item).values(items_data)
            upsert_stmt = stmt.on_conflict_do_update(
                index_elements=[Item.id],
                set_={
                    "name_ru": stmt.excluded.name_ru,
                    "name_en": stmt.excluded.name_en,
                    "category": stmt.excluded.category,
                    "is_barterable": stmt.excluded.is_barterable,
                },
            )

            await self.session.execute(upsert_stmt)

            if recipes_list:
                self.session.add_all(recipes_list)

            await self.session.flush()

    async def get_current_commit_sha(self) -> str | None:
        stmt = select(StalcraftVersion.version_sha).where(
            StalcraftVersion.id == "latest"
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_commit_sha(self, sha: str):
        new_version = StalcraftVersion(id="latest", version_sha=sha)
        await self.session.merge(new_version)
        await self.session.commit()
