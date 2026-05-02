from aiogram.filters.callback_data import CallbackData


class MenuClick(CallbackData, prefix="menu"):
    target: str
    back_to: str = "main"


class MenuTaskNav(CallbackData, prefix="menu_nav"):
    task_idx: int


class AddTaskClick(CallbackData, prefix="add_task"):
    item_id: str
    offer_idx: int


class SearchItem(CallbackData, prefix="select_task_item"):
    item_id: str


class RecipeNav(CallbackData, prefix="recipe_nav"):
    item_id: str
    idx: str


class LanguageClick(CallbackData, prefix="lang"):
    locale: str
