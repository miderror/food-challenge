from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    waiting_for_contact = State()
    waiting_for_fio = State()
    waiting_for_hw = State()
