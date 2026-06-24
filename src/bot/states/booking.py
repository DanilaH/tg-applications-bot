from aiogram.filters.state import State, StatesGroup


class BookingState(StatesGroup):
    choosing_service = State()
    entering_name = State()
