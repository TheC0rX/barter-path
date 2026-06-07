from enum import StrEnum
from aiogram.filters.callback_data import CallbackData


# --- ACTIONS
class MenuAction(StrEnum):
    MENU = "menu"
    FINISH_TASK = "finish_task"
    ADD_TASK = "add_task"
    DELETE_TASK = "delete_task"
    ACTIVATE_DISCOUNT = "discount"
    MANAGE_RESOURCES = "resources"
    SETTINGS = "settings"


class DiscountAction(StrEnum):
    OFFER = "offer"
    CONFIRM = "confirm"


class AddTaskAction(StrEnum):
    CONFIRM = "confirm"
    SEARCH = "search"
    NAVIGATION = "nav"


class ResourceCalcAction(StrEnum):
    ADD = "add"
    RESET = "reset"
    CONFIRM = "confirm"


# --- MENU
class MenuClick(CallbackData, prefix="menu"):
    target: MenuAction
    task_id: int = 0


class MenuNav(CallbackData, prefix="menu_nav"):
    task_index: int


class FinishTaskClick(CallbackData, prefix="finish_task"):
    task_id: int


class AddTaskClick(CallbackData, prefix="add_task"):
    action: AddTaskAction
    item_id: str
    offer_idx: int = 0
    idx: int = 0
    prev_id: str = ""


class DeleteTaskClick(CallbackData, prefix="delete_task"):
    task_id: int


class DiscountClick(CallbackData, prefix="discount"):
    action: DiscountAction
    task_id: int
    discount: int


class ResourceClick(CallbackData, prefix="resource"):
    task_id: int
    ing_id: str


class ResourceCalc(CallbackData, prefix="res_calc"):
    action: ResourceCalcAction
    task_id: int
    ing_id: str
    value: int = 0


# --- SETTINGS
class LanguageClick(CallbackData, prefix="lang"):
    locale: str
