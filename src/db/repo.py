from sqlalchemy.ext.asyncio import AsyncSession
from .models import User


class UserRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_user(self, user_id: int, locale: str):
        user = User(user_id=user_id, locale=locale)  # type: ignore
        await self.session.merge(user)
        await self.session.commit()
