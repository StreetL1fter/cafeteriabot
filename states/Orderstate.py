from aiogram.fsm.state import State,StatesGroup

class OrderState(StatesGroup):
    cart = State()
    waiting_for_name = State()
    waiting_for_phone = State()