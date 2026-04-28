from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs

from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import (
    BIGINT,
    VARCHAR,
    TIMESTAMP,
)


class Base(DeclarativeBase, AsyncAttrs): ...


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=False)
    locale: Mapped[str] = mapped_column(VARCHAR(2), default="en")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
