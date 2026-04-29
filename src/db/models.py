from typing import List

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs

from datetime import datetime
from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import (
    INTEGER,
    BIGINT,
    VARCHAR,
    TIMESTAMP,
)


class Base(DeclarativeBase, AsyncAttrs): ...


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=False)
    locale: Mapped[str] = mapped_column(VARCHAR(2), default="en")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )


class Item(Base):
    __tablename__ = "items"

    id: Mapped[str] = mapped_column(VARCHAR, primary_key=True)
    category: Mapped[str] = mapped_column(VARCHAR, index=True)

    name_ru: Mapped[str] = mapped_column(VARCHAR)
    name_en: Mapped[str] = mapped_column(VARCHAR)

    recipe_results: Mapped[List["Recipe"]] = relationship(
        "Recipe", foreign_keys="[Recipe.item_id]", back_populates="result_item"
    )


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[str] = mapped_column(ForeignKey("items.id", ondelete="CASCADE"))
    ingredient_id: Mapped[str] = mapped_column(
        ForeignKey("items.id", ondelete="CASCADE")
    )
    amount: Mapped[int] = mapped_column(INTEGER)

    result_item: Mapped["Item"] = relationship(
        "Item", foreign_keys=[item_id], back_populates="recipe_results"
    )
    ingredient_item: Mapped["Item"] = relationship("Item", foreign_keys=[ingredient_id])
