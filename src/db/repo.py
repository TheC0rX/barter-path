from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func, delete, update
from sqlalchemy.orm import joinedload

from .models import User, Item, Recipe, UserTask


class UserRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user(self, user_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.user_id == user_id))
        return result.scalar_one_or_none()

    async def add_user(self, user_id: int, locale: str) -> None:
        user = User(user_id=user_id, locale=locale)  # type: ignore
        await self.session.merge(user)
        await self.session.commit()

    async def get_user_tasks_count(self, user_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(UserTask)
            .where(UserTask.user_id == user_id)
        )
        result = await self.session.execute(stmt)

        return result.scalar() or 0

    async def check_task_exists(self, user_id: int, item_id: str) -> bool:
        stmt = select(UserTask).where(
            UserTask.user_id == user_id, UserTask.item_id == item_id
        )
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none() is not None

    async def has_tasks(self, user_id: int) -> bool:
        stmt = select(UserTask).where(UserTask.user_id == user_id).limit(1)
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none() is not None

    async def get_user_tasks(self, user_id: int):
        stmt = (
            select(UserTask)
            .options(joinedload(UserTask.item))
            .where(UserTask.user_id == user_id)
            .order_by(UserTask.id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add_task(self, user_id: int, item_id: str, offer_idx: int):
        new_task = UserTask(user_id=user_id, item_id=item_id, offer_idx=offer_idx)
        self.session.add(new_task)
        await self.session.commit()

    async def drop_task(self, task_id: int):
        stmt = delete(UserTask).where(UserTask.id == task_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def activate_discount(self, task_id: int, discount: int):
        stmt = update(UserTask).where(UserTask.id == task_id).values(discount=discount)
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_task_by_task_id(self, task_id: int):
        stmt = select(UserTask).where(UserTask.id == task_id)
        result = await self.session.execute(stmt)

        return result.scalar_one()

    async def get_item_name_by_task_id(self, task_id: int, locale: str) -> str:
        name_col = Item.name_ru if locale == "ru" else Item.name_en
        stmt = (
            select(name_col)
            .join(UserTask, UserTask.item_id == Item.id)
            .where(UserTask.id == task_id)
        )

        result = await self.session.execute(stmt)
        return result.scalar_one()


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
            .order_by(Recipe.offer_index)
        )

        result = await self.session.execute(stmt)
        return result.all()

    async def get_item(self, item_id: str) -> Item | None:
        return await self.session.get(Item, item_id)
