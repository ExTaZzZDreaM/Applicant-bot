from aiogram.fsm.state import State, StatesGroup

class StatusFSM(StatesGroup):
    waiting_category = State()
    waiting_iin = State()