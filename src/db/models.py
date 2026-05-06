from typing import List

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs

from datetime import datetime
from sqlalchemy import func, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import (
    INTEGER,
    BIGINT,
    VARCHAR,
    BOOLEAN,
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

    tasks: Mapped[List["UserTask"]] = relationship(
        "UserTask", back_populates="user", cascade="all, delete-orphan"
    )


class UserTask(Base):
    __tablename__ = "user_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("users.user_id", ondelete="CASCADE"), index=True
    )
    item_id: Mapped[str] = mapped_column(
        ForeignKey("items.id", ondelete="CASCADE"), index=True
    )
    offer_idx: Mapped[int] = mapped_column(INTEGER, default=0)
    discount: Mapped[int] = mapped_column(INTEGER, default=0)

    user: Mapped["User"] = relationship("User", back_populates="tasks")
    item: Mapped["Item"] = relationship("Item", back_populates="user_tasks")

    __table_args__ = (
        UniqueConstraint("user_id", "item_id", "offer_idx", name="uq_user_item_offer"),
    )


class Item(Base):
    __tablename__ = "items"

    id: Mapped[str] = mapped_column(VARCHAR(8), primary_key=True)
    category: Mapped[str] = mapped_column(VARCHAR(64), index=True)
    name_ru: Mapped[str] = mapped_column(VARCHAR(128))
    name_en: Mapped[str] = mapped_column(VARCHAR(128))
    is_barterable: Mapped[bool] = mapped_column(BOOLEAN, default=False, index=True)

    user_tasks: Mapped[List["UserTask"]] = relationship(
        "UserTask", back_populates="item"
    )
    recipe_results: Mapped[List["Recipe"]] = relationship(
        "Recipe",
        foreign_keys="[Recipe.item_id]",
        back_populates="result_item",
        cascade="all, delete-orphan",
    )
    used_in_recipes: Mapped[List["Recipe"]] = relationship(
        "Recipe",
        foreign_keys="[Recipe.ingredient_id]",
        back_populates="ingredient_item",
    )


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[str] = mapped_column(
        ForeignKey("items.id", ondelete="CASCADE"), index=True
    )
    ingredient_id: Mapped[str] = mapped_column(
        ForeignKey("items.id", ondelete="CASCADE"), index=True
    )
    amount: Mapped[int] = mapped_column(INTEGER)
    offer_index: Mapped[int] = mapped_column(INTEGER, default=0)

    result_item: Mapped["Item"] = relationship(
        "Item", foreign_keys=[item_id], back_populates="recipe_results"
    )
    ingredient_item: Mapped["Item"] = relationship(
        "Item", foreign_keys=[ingredient_id], back_populates="used_in_recipes"
    )

    __table_args__ = (
        UniqueConstraint(
            "item_id", "ingredient_id", "offer_index", name="uq_recipe_ingredient"
        ),
    )
