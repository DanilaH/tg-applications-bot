from aiogram.filters.state import State, StatesGroup


class BookingState(StatesGroup):
    choosing_service = State()
    entering_name = State()
    entering_phone = State()
    entering_comment = State()
    confirming = State()
    ready_to_submit = State()
