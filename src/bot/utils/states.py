from aiogram.fsm.state import State, StatesGroup


class AddTaskStates(StatesGroup):
    wait_for_item_name = State()


class ResourceCalcStates(StatesGroup):
    wait_for_amount = State()
