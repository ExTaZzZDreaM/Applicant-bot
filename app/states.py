from aiogram.fsm.state import State, StatesGroup

class StatusFSM(StatesGroup):
    waiting_iin = State()