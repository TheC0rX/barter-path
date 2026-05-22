from enum import StrEnum
from aiogram.filters.callback_data import CallbackData


# --- ACTIONS
class MenuAction(StrEnum):
    NAVIGATION = "navigation"
    MENU = "menu"
    FINISH_TASK = "finish_task"
    ADD_TASK = "add_task"
    DELETE_TASK = "delete_task"
    ACTIVATE_DISCOUNT = "activate_discount"
    MANAGE_RESOURCES = "manage_resources"
    SETTINGS = "settings"


class DiscountAction(StrEnum):
    OFFER = "offer"
    ACTIVATE = "activate"


class AddTaskAction(StrEnum):
    ADD_TASK = "add_task"
    SEARCH = "search"
    NAVIGATION = "navigation"


# --- MENU
class MenuClick(CallbackData, prefix="menu"):
    target: MenuAction
    task_id: int = 0
    task_idx: int = 0


class FinishTaskClick(CallbackData, prefix="finish_task"):
    task_id: int


class AddTaskClick(CallbackData, prefix="add_task"):
    action: AddTaskAction
    item_id: str
    offer_idx: int = 0
    idx: str = ""


class DeleteTaskClick(CallbackData, prefix="delete_task"):
    task_id: int


class DiscountClick(CallbackData, prefix="discount"):
    action: DiscountAction
    task_id: int
    discount: int


class ResourceClick(CallbackData, prefix="resource"):
    action: str
    task_id: int
    ingredient_id: str


# --- SETTINGS
class LanguageClick(CallbackData, prefix="lang"):
    locale: str
