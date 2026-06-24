from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.keyboards.booking import build_service_keyboard
from bot.keyboards.main_menu import build_main_menu
from bot.services.catalog import get_service
from bot.states.booking import BookingState

SERVICE_PROMPT = "Выберите услугу:"
NAME_PROMPT_TEMPLATE = "Вы выбрали: {service_name}\n\nТеперь введите ваше имя:"


async def handle_booking_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(BookingState.choosing_service)
    await callback.message.edit_text(
        SERVICE_PROMPT,
        reply_markup=build_service_keyboard(),
    )
    await callback.answer()


async def handle_service_selection(callback: CallbackQuery, state: FSMContext) -> None:
    service_id = callback.data.removeprefix("booking:service:")

    service = get_service(service_id)
    if service is None:
        await callback.answer("Эта услуга недоступна", show_alert=True)
        return

    await state.update_data(service_id=service.id, service_name=service.name)
    await state.set_state(BookingState.entering_name)
    await callback.message.edit_text(
        NAME_PROMPT_TEMPLATE.format(service_name=service.name)
    )
    await callback.answer()


async def handle_booking_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    from bot.handlers.start import WELCOME_TEXT

    await callback.message.edit_text(
        WELCOME_TEXT,
        reply_markup=build_main_menu(),
    )
    await callback.answer()


def create_booking_router() -> Router:
    router = Router(name=__name__)

    router.callback_query.register(
        handle_booking_start,
        F.data == "booking:start",
    )
    router.callback_query.register(
        handle_service_selection,
        StateFilter(BookingState.choosing_service),
        F.data.startswith("booking:service:"),
    )
    router.callback_query.register(
        handle_booking_cancel,
        F.data == "booking:cancel",
    )

    return router
