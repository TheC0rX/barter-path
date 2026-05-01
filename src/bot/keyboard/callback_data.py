from aiogram.filters.callback_data import CallbackData


class MenuClick(CallbackData, prefix="menu"):
    target: str
    back_to: str = "main"


class RecipeNav(CallbackData, prefix="recipe_nav"):
    item_id: str
    idx: str


class LanguageClick(CallbackData, prefix="lang"):
    locale: str
