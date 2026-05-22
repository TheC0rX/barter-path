from enum import StrEnum
from aiogram.filters.callback_data import CallbackData


class MenuAction(StrEnum):
    MENU = "menu"
    FINISH_TASK = "finish_task"
    ADD_TASK = "add_task"
    DELETE_TASK = "delete_task"
    ACTIVATE_DISCOUNT = "activate_discount"
    MANAGE_RESOURCES = "manage_resources"
    SETTINGS = "settings"


class MenuClick(CallbackData, prefix="menu"):
    target: MenuAction
    task_id: int = 0
    back_to: str = "main"


class MenuTaskNav(CallbackData, prefix="menu_nav"):
    task_idx: int


class FinishTaskClick(CallbackData, prefix="finish_task"):
    task_id: int


class AddTaskClick(CallbackData, prefix="add_task"):
    item_id: str
    offer_idx: int


class SearchItem(CallbackData, prefix="select_task_item"):
    item_id: str


class DeleteTaskClick(CallbackData, prefix="delete_task"):
    task_id: int


class DiscountOfferClick(CallbackData, prefix="discount_offer"):
    task_id: int
    discount: int


class ActivateDiscountClick(CallbackData, prefix="activate_discount"):
    task_id: int
    discount: int


class RecipeNav(CallbackData, prefix="recipe_nav"):
    item_id: str
    idx: str


class ResourceClick(CallbackData, prefix="resource"):
    action: str
    task_id: int
    ingredient_id: str


class LanguageClick(CallbackData, prefix="lang"):
    locale: str
