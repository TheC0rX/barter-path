from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from .models import User, Item, Recipe


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
