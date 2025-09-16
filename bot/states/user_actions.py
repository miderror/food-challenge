from aiogram.fsm.state import State, StatesGroup


class UserActions(StatesGroup):
    suggesting_product = State()
