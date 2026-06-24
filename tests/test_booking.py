import asyncio
from unittest.mock import AsyncMock

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from bot.handlers.booking import (
    NAME_PROMPT_TEMPLATE,
    SERVICE_PROMPT,
    handle_booking_cancel,
    handle_booking_start,
    handle_service_selection,
)
from bot.handlers.start import WELCOME_TEXT
from bot.keyboards.booking import build_service_keyboard
from bot.keyboards.main_menu import build_main_menu
from bot.services.catalog import ALLOWED_SERVICE_IDS, ALLOWED_SERVICES, get_service
from bot.states.booking import BookingState


def _make_fsm_context() -> FSMContext:
    """Create a clean FSMContext synchronously by running async internals."""
    storage = MemoryStorage()
    ctx = FSMContext(storage=storage, key="test_user")
    asyncio.run(ctx.clear())
    return ctx


# ---------------------------------------------------------------------------
# Catalog tests
# ---------------------------------------------------------------------------


def test_catalog_contains_exactly_four_services() -> None:
    assert len(ALLOWED_SERVICES) == 4


def test_catalog_has_expected_service_ids() -> None:
    expected = {"men_haircut", "beard_trim", "combo", "consultation"}
    assert set(ALLOWED_SERVICE_IDS) == expected


def test_get_service_returns_service_for_valid_id() -> None:
    service = get_service("men_haircut")
    assert service is not None
    assert service.id == "men_haircut"
    assert service.name == "Мужская стрижка"


def test_get_service_returns_none_for_invalid_id() -> None:
    assert get_service("nonexistent") is None


# ---------------------------------------------------------------------------
# Keyboard tests
# ---------------------------------------------------------------------------


def test_service_keyboard_contains_all_services_and_cancel() -> None:
    keyboard = build_service_keyboard()

    # 4 services + 1 cancel row
    assert len(keyboard.inline_keyboard) == 5

    # Check each service button
    for i, service in enumerate(ALLOWED_SERVICES):
        button = keyboard.inline_keyboard[i][0]
        assert button.text == service.name
        assert button.callback_data == f"booking:service:{service.id}"

    # Check cancel button
    cancel_button = keyboard.inline_keyboard[-1][0]
    assert cancel_button.text == "Отмена"
    assert cancel_button.callback_data == "booking:cancel"


# ---------------------------------------------------------------------------
# FSM transition tests
# ---------------------------------------------------------------------------


@pytest.fixture
def callback() -> AsyncMock:
    cb = AsyncMock()
    cb.message = AsyncMock()
    return cb


@pytest.fixture
def state() -> FSMContext:
    return _make_fsm_context()


def test_booking_start_sets_choosing_service_and_edits_message(
    callback: AsyncMock,
    state: FSMContext,
) -> None:
    asyncio.run(handle_booking_start(callback, state))

    current_state = asyncio.run(state.get_state())
    assert current_state == BookingState.choosing_service

    callback.message.edit_text.assert_awaited_once_with(
        SERVICE_PROMPT,
        reply_markup=build_service_keyboard(),
    )
    callback.answer.assert_awaited_once()


def test_valid_service_selection_saves_data_and_transitions(
    callback: AsyncMock,
    state: FSMContext,
) -> None:
    # Start from choosing_service
    asyncio.run(state.set_state(BookingState.choosing_service))
    callback.data = "booking:service:combo"

    asyncio.run(handle_service_selection(callback, state))

    data = asyncio.run(state.get_data())
    assert data["service_id"] == "combo"
    assert data["service_name"] == "Стрижка + борода"

    current_state = asyncio.run(state.get_state())
    assert current_state == BookingState.entering_name

    callback.message.edit_text.assert_awaited_once_with(
        NAME_PROMPT_TEMPLATE.format(service_name="Стрижка + борода"),
    )
    callback.answer.assert_awaited_once()


def test_invalid_service_shows_alert_and_keeps_choosing_service(
    callback: AsyncMock,
    state: FSMContext,
) -> None:
    # Start from choosing_service
    asyncio.run(state.set_state(BookingState.choosing_service))
    callback.data = "booking:service:unknown_service"

    asyncio.run(handle_service_selection(callback, state))

    data = asyncio.run(state.get_data())
    assert data == {}

    current_state = asyncio.run(state.get_state())
    assert current_state == BookingState.choosing_service

    callback.answer.assert_awaited_once_with(
        "Эта услуга недоступна",
        show_alert=True,
    )


def test_cancel_clears_state_and_returns_main_menu(
    callback: AsyncMock,
    state: FSMContext,
) -> None:
    # Set some state first
    asyncio.run(state.set_state(BookingState.choosing_service))
    asyncio.run(state.update_data(service_id="men_haircut"))

    asyncio.run(handle_booking_cancel(callback, state))

    data = asyncio.run(state.get_data())
    assert data == {}

    current_state = asyncio.run(state.get_state())
    assert current_state is None

    callback.message.edit_text.assert_awaited_once_with(
        WELCOME_TEXT,
        reply_markup=build_main_menu(),
    )
    callback.answer.assert_awaited_once()


# ---------------------------------------------------------------------------
# Router registration tests
# ---------------------------------------------------------------------------


def test_booking_router_is_registered_in_dispatcher() -> None:
    from bot.loader import create_dispatcher

    dispatcher = create_dispatcher()

    # Should have start + booking routers
    assert len(dispatcher.sub_routers) == 2

    booking_router = dispatcher.sub_routers[1]
    assert booking_router.name == "bot.handlers.booking"
    # 3 callback handlers: start, service selection, cancel
    assert len(booking_router.callback_query.handlers) == 3


def test_dispatcher_can_be_created_multiple_times() -> None:
    from bot.loader import create_dispatcher

    d1 = create_dispatcher()
    d2 = create_dispatcher()

    assert len(d1.sub_routers) == 2
    assert len(d2.sub_routers) == 2
    assert d1.sub_routers[1].name == d2.sub_routers[1].name
