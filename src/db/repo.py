from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .models import User


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
