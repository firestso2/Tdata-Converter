from aiogram.fsm.state import State, StatesGroup

class AuthStates(StatesGroup):
    waiting_phone    = State()
    waiting_code     = State()
    waiting_password = State()
    authenticated    = State()
