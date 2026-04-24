from aiogram.fsm.state import State, StatesGroup


class AuthStates(StatesGroup):
    choosing_lang    = State()
    waiting_phone    = State()
    waiting_code     = State()
    waiting_password = State()
    authenticated    = State()
