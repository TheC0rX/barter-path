from enum import StrEnum
from aiogram.filters.callback_data import CallbackData


# --- ACTIONS
class MenuAction(StrEnum):
    MENU = "m"
    FINISH_TASK = "ft"
    ADD_TASK = "at"
    DELETE_TASK = "dt"
    ACTIVATE_DISCOUNT = "dc"
    MANAGE_RESOURCES = "rs"
    SETTINGS = "st"


class DiscountAction(StrEnum):
    OFFER = "o"
    CONFIRM = "c"


class AddTaskAction(StrEnum):
    CONFIRM = "c"
    SEARCH = "s"
    NAVIGATION = "n"


class ResourceCalcAction(StrEnum):
    ADD = "a"
    RESET = "r"
    CONFIRM = "c"


# --- MENU
class MenuClick(CallbackData, prefix="mn"):
    target: MenuAction
    t_id: int = 0
    t_idx: int | None = None


class MenuNav(CallbackData, prefix="mn_nv"):
    idx: int


class FinishTaskClick(CallbackData, prefix="fn_tk"):
    t_id: int


class AddTaskClick(CallbackData, prefix="ad_tk"):
    action: AddTaskAction
    t_id: int
    item_id: str
    o_idx: int = 0
    idx: int = 0
    prev_id: str = ""


class DeleteTaskClick(CallbackData, prefix="dl_tk"):
    t_id: int


class DiscountClick(CallbackData, prefix="ds_tk"):
    action: DiscountAction
    t_id: int
    dc: int


class ResourceClick(CallbackData, prefix="rsc"):
    t_id: int
    ing_id: str


class ResourceCalc(CallbackData, prefix="rcc"):
    action: ResourceCalcAction
    t_id: int
    ing_id: str
    val: int = 0


# --- SETTINGS
class LanguageClick(CallbackData, prefix="lng"):
    t_id: int
    loc: str
