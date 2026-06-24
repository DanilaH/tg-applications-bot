import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from bot.handlers.booking import (
    CANCEL_MESSAGE,
    COMMENT_PROMPT,
    CONFIRMING_MESSAGE,
    EMPTY_COMMENT_ERROR,
    NAME_PROMPT_TEMPLATE,
    NON_TEXT_ERROR,
    PHONE_PROMPT,
    SERVICE_PROMPT,
    _normalize_name,
    handle_booking_start,
    handle_comment_input,
    handle_contact,
    handle_inline_cancel,
    handle_name_input,
    handle_non_text_comment,
    handle_non_text_name,
    handle_non_text_phone,
    handle_phone_text,
    handle_service_selection,
    handle_skip_comment,
    handle_text_cancel,
)
from bot.handlers.start import WELCOME_TEXT
from bot.keyboards.booking import (
    build_comment_keyboard,
    build_name_keyboard,
    build_phone_keyboard,
    build_remove_reply,
    build_service_keyboard,
)
from bot.keyboards.main_menu import build_main_menu
from bot.services.catalog import ALLOWED_SERVICE_IDS, ALLOWED_SERVICES, get_service
from bot.states.booking import BookingState
from bot.utils.phone import normalize_phone


def _make_fsm_context() -> FSMContext:
    storage = MemoryStorage()
    ctx = FSMContext(storage=storage, key="test_user")
    asyncio.run(ctx.clear())
    return ctx


# ===================================================================
# Phone normalization
# ===================================================================


class TestNormalizePhone:
    def test_international_with_plus(self) -> None:
        assert normalize_phone("+7 999 123-45-67") == "+79991234567"

    def test_international_without_plus(self) -> None:
        assert normalize_phone("79991234567") == "79991234567"

    def test_with_parentheses(self) -> None:
        assert normalize_phone("+1 (212) 555-0198") == "+12125550198"

    def test_rejects_letters(self) -> None:
        assert normalize_phone("abc123") is None

    def test_rejects_too_short(self) -> None:
        assert normalize_phone("12345") is None

    def test_rejects_too_long(self) -> None:
        assert normalize_phone("+" + "1" * 16) is None

    def test_accepts_15_digits(self) -> None:
        assert normalize_phone("+" + "1" * 15) == "+" + "1" * 15

    def test_accepts_10_digits(self) -> None:
        assert normalize_phone("1234567890") == "1234567890"

    def test_whitespace_only(self) -> None:
        assert normalize_phone("   ") is None

    def test_empty_string(self) -> None:
        assert normalize_phone("") is None

    def test_rejects_multiple_plus_signs(self) -> None:
        assert normalize_phone("++79991234567") is None

    def test_rejects_plus_in_middle(self) -> None:
        assert normalize_phone("7999+1234567") is None


# ===================================================================
# Name normalization
# ===================================================================


class TestNormalizeName:
    def test_valid_name(self) -> None:
        assert _normalize_name("  Иван  Петров  ") == "Иван Петров"

    def test_too_short(self) -> None:
        assert _normalize_name("A") is None

    def test_too_long(self) -> None:
        assert _normalize_name("A" * 81) is None

    def test_exactly_2_chars(self) -> None:
        assert _normalize_name("AB") == "AB"

    def test_exactly_80_chars(self) -> None:
        assert _normalize_name("A" * 80) == "A" * 80

    def test_whitespace_only(self) -> None:
        assert _normalize_name("   ") is None


# ===================================================================
# Catalog tests
# ===================================================================


class TestCatalog:
    def test_contains_exactly_four_services(self) -> None:
        assert len(ALLOWED_SERVICES) == 4

    def test_has_expected_service_ids(self) -> None:
        expected = {"men_haircut", "beard_trim", "combo", "consultation"}
        assert set(ALLOWED_SERVICE_IDS) == expected

    def test_get_service_returns_service_for_valid_id(self) -> None:
        service = get_service("men_haircut")
        assert service is not None
        assert service.id == "men_haircut"
        assert service.name == "Мужская стрижка"

    def test_get_service_returns_none_for_invalid_id(self) -> None:
        assert get_service("nonexistent") is None


# ===================================================================
# Keyboard tests
# ===================================================================


class TestKeyboards:
    def test_service_keyboard_contains_all_services_and_cancel(self) -> None:
        keyboard = build_service_keyboard()
        assert len(keyboard.inline_keyboard) == 5

        for i, service in enumerate(ALLOWED_SERVICES):
            button = keyboard.inline_keyboard[i][0]
            assert button.text == service.name
            assert button.callback_data == f"booking:service:{service.id}"

        cancel_button = keyboard.inline_keyboard[-1][0]
        assert cancel_button.text == "Отмена"
        assert cancel_button.callback_data == "booking:cancel"

    def test_name_keyboard_has_cancel_button(self) -> None:
        """Name input step must have an inline cancel button."""
        keyboard = build_name_keyboard()
        assert len(keyboard.inline_keyboard) == 1
        button = keyboard.inline_keyboard[0][0]
        assert button.text == "Отмена"
        assert button.callback_data == "booking:cancel"

    def test_phone_keyboard_has_contact_and_cancel(self) -> None:
        kb = build_phone_keyboard()
        assert len(kb.keyboard) == 2
        assert kb.keyboard[0][0].text == "Отправить телефон"
        assert kb.keyboard[0][0].request_contact is True
        assert kb.keyboard[1][0].text == "Отмена"

    def test_comment_keyboard_has_skip_and_cancel(self) -> None:
        kb = build_comment_keyboard()
        assert len(kb.keyboard) == 2
        assert kb.keyboard[0][0].text == "Пропустить"
        assert kb.keyboard[1][0].text == "Отмена"


# ===================================================================
# Fixtures
# ===================================================================


@pytest.fixture
def callback() -> AsyncMock:
    cb = AsyncMock()
    cb.message = AsyncMock()
    return cb


@pytest.fixture
def message() -> AsyncMock:
    msg = AsyncMock()
    msg.from_user = MagicMock()
    msg.from_user.id = 123
    return msg


@pytest.fixture
def state() -> FSMContext:
    return _make_fsm_context()


# ===================================================================
# Service selection (Phase 2)
# ===================================================================


class TestServiceSelection:
    def test_booking_start_sets_choosing_service(
        self, callback: AsyncMock, state: FSMContext
    ) -> None:
        asyncio.run(handle_booking_start(callback, state))
        assert asyncio.run(state.get_state()) == BookingState.choosing_service
        callback.message.edit_text.assert_awaited_once_with(
            SERVICE_PROMPT, reply_markup=build_service_keyboard()
        )
        callback.answer.assert_awaited_once()

    def test_valid_service_saves_data_and_transitions(
        self, callback: AsyncMock, state: FSMContext
    ) -> None:
        asyncio.run(state.set_state(BookingState.choosing_service))
        callback.data = "booking:service:combo"
        asyncio.run(handle_service_selection(callback, state))
        data = asyncio.run(state.get_data())
        assert data["service_id"] == "combo"
        assert data["service_name"] == "Стрижка + борода"
        assert asyncio.run(state.get_state()) == BookingState.entering_name
        callback.message.edit_text.assert_awaited_once_with(
            NAME_PROMPT_TEMPLATE.format(service_name="Стрижка + борода"),
            reply_markup=build_name_keyboard(),
        )

    def test_invalid_service_keeps_choosing_service(
        self, callback: AsyncMock, state: FSMContext
    ) -> None:
        asyncio.run(state.set_state(BookingState.choosing_service))
        callback.data = "booking:service:unknown_service"
        asyncio.run(handle_service_selection(callback, state))
        assert asyncio.run(state.get_data()) == {}
        assert asyncio.run(state.get_state()) == BookingState.choosing_service
        callback.answer.assert_awaited_once_with(
            "Эта услуга недоступна", show_alert=True
        )


# ===================================================================
# Cancel
# ===================================================================


class TestCancel:
    @pytest.mark.parametrize(
        "target_state",
        [
            BookingState.choosing_service,
            BookingState.entering_name,
            BookingState.entering_phone,
            BookingState.entering_comment,
        ],
    )
    def test_inline_cancel_clears_state_on_each_step(
        self, callback: AsyncMock, state: FSMContext, target_state
    ) -> None:
        asyncio.run(state.set_state(target_state))
        asyncio.run(state.update_data(service_id="men_haircut"))
        asyncio.run(handle_inline_cancel(callback, state))
        assert asyncio.run(state.get_data()) == {}
        assert asyncio.run(state.get_state()) is None
        callback.message.edit_text.assert_awaited_once_with(
            WELCOME_TEXT, reply_markup=build_main_menu()
        )
        callback.answer.assert_awaited_once()

    @pytest.mark.parametrize(
        "target_state",
        [
            BookingState.entering_name,
            BookingState.entering_phone,
            BookingState.entering_comment,
        ],
    )
    def test_text_cancel_clears_state_on_each_step(
        self, message: AsyncMock, state: FSMContext, target_state
    ) -> None:
        asyncio.run(state.set_state(target_state))
        asyncio.run(state.update_data(service_id="men_haircut"))
        asyncio.run(handle_text_cancel(message, state))
        assert asyncio.run(state.get_data()) == {}
        assert asyncio.run(state.get_state()) is None
        # First call removes reply keyboard
        message.answer.assert_any_await(
            CANCEL_MESSAGE, reply_markup=build_remove_reply()
        )
        # Second call shows main menu
        message.answer.assert_any_await(
            WELCOME_TEXT, reply_markup=build_main_menu()
        )


# ===================================================================
# Name input
# ===================================================================


class TestNameInput:
    def test_valid_name_saves_and_transitions(
        self, message: AsyncMock, state: FSMContext
    ) -> None:
        asyncio.run(state.set_state(BookingState.entering_name))
        message.text = "  Иван  "
        asyncio.run(handle_name_input(message, state))
        data = asyncio.run(state.get_data())
        assert data["customer_name"] == "Иван"
        assert asyncio.run(state.get_state()) == BookingState.entering_phone
        message.answer.assert_awaited_once_with(
            PHONE_PROMPT, reply_markup=build_phone_keyboard()
        )

    def test_empty_name_shows_error_and_keeps_state(
        self, message: AsyncMock, state: FSMContext
    ) -> None:
        asyncio.run(state.set_state(BookingState.entering_name))
        message.text = "  "
        asyncio.run(handle_name_input(message, state))
        assert asyncio.run(state.get_data()) == {}
        assert asyncio.run(state.get_state()) == BookingState.entering_name
        message.answer.assert_awaited_once()

    def test_too_long_name_shows_error_and_keeps_state(
        self, message: AsyncMock, state: FSMContext
    ) -> None:
        asyncio.run(state.set_state(BookingState.entering_name))
        message.text = "A" * 81
        asyncio.run(handle_name_input(message, state))
        assert asyncio.run(state.get_data()) == {}
        assert asyncio.run(state.get_state()) == BookingState.entering_name

    def test_non_text_name_shows_error(
        self, message: AsyncMock, state: FSMContext
    ) -> None:
        asyncio.run(state.set_state(BookingState.entering_name))
        asyncio.run(handle_non_text_name(message))
        assert asyncio.run(state.get_state()) == BookingState.entering_name
        message.answer.assert_awaited_once_with(NON_TEXT_ERROR)


# ===================================================================
# Phone input
# ===================================================================


class TestPhoneInput:
    def test_valid_phone_text_saves_and_transitions(
        self, message: AsyncMock, state: FSMContext
    ) -> None:
        asyncio.run(state.set_state(BookingState.entering_phone))
        message.text = "+7 999 123-45-67"
        asyncio.run(handle_phone_text(message, state))
        data = asyncio.run(state.get_data())
        assert data["phone"] == "+79991234567"
        assert asyncio.run(state.get_state()) == BookingState.entering_comment
        message.answer.assert_awaited_once_with(
            COMMENT_PROMPT, reply_markup=build_comment_keyboard()
        )

    def test_invalid_phone_shows_error_and_keeps_state(
        self, message: AsyncMock, state: FSMContext
    ) -> None:
        asyncio.run(state.set_state(BookingState.entering_phone))
        message.text = "abc"
        asyncio.run(handle_phone_text(message, state))
        assert asyncio.run(state.get_data()) == {}
        assert asyncio.run(state.get_state()) == BookingState.entering_phone

    def test_own_contact_saves_and_transitions(
        self, message: AsyncMock, state: FSMContext
    ) -> None:
        asyncio.run(state.set_state(BookingState.entering_phone))
        message.contact = MagicMock()
        message.contact.user_id = 123
        message.contact.phone_number = "+79991234567"
        asyncio.run(handle_contact(message, state))
        data = asyncio.run(state.get_data())
        assert data["phone"] == "+79991234567"
        assert asyncio.run(state.get_state()) == BookingState.entering_comment

    def test_foreign_contact_rejected(
        self, message: AsyncMock, state: FSMContext
    ) -> None:
        asyncio.run(state.set_state(BookingState.entering_phone))
        message.contact = MagicMock()
        message.contact.user_id = 999
        message.contact.phone_number = "+79991234567"
        asyncio.run(handle_contact(message, state))
        assert asyncio.run(state.get_data()) == {}
        assert asyncio.run(state.get_state()) == BookingState.entering_phone
        message.answer.assert_awaited_once()

    def test_non_text_phone_says_error(
        self, message: AsyncMock, state: FSMContext
    ) -> None:
        asyncio.run(state.set_state(BookingState.entering_phone))
        asyncio.run(handle_non_text_phone(message))
        assert asyncio.run(state.get_state()) == BookingState.entering_phone
        message.answer.assert_awaited_once()


# ===================================================================
# Comment input
# ===================================================================


class TestCommentInput:
    def test_valid_comment_saves_and_transitions(
        self, message: AsyncMock, state: FSMContext
    ) -> None:
        asyncio.run(state.set_state(BookingState.entering_comment))
        message.text = "Хочу после 18:00"
        asyncio.run(handle_comment_input(message, state))
        data = asyncio.run(state.get_data())
        assert data["comment"] == "Хочу после 18:00"
        assert asyncio.run(state.get_state()) == BookingState.confirming
        message.answer.assert_awaited_once_with(
            CONFIRMING_MESSAGE, reply_markup=build_remove_reply()
        )

    def test_empty_comment_shows_error(
        self, message: AsyncMock, state: FSMContext
    ) -> None:
        asyncio.run(state.set_state(BookingState.entering_comment))
        message.text = "   "
        asyncio.run(handle_comment_input(message, state))
        assert asyncio.run(state.get_data()) == {}
        assert asyncio.run(state.get_state()) == BookingState.entering_comment
        message.answer.assert_awaited_once_with(EMPTY_COMMENT_ERROR)

    def test_too_long_comment_shows_error(
        self, message: AsyncMock, state: FSMContext
    ) -> None:
        asyncio.run(state.set_state(BookingState.entering_comment))
        message.text = "A" * 501
        asyncio.run(handle_comment_input(message, state))
        assert asyncio.run(state.get_data()) == {}
        assert asyncio.run(state.get_state()) == BookingState.entering_comment

    def test_skip_saves_none_and_transitions(
        self, message: AsyncMock, state: FSMContext
    ) -> None:
        asyncio.run(state.set_state(BookingState.entering_comment))
        asyncio.run(handle_skip_comment(message, state))
        data = asyncio.run(state.get_data())
        assert data["comment"] is None
        assert asyncio.run(state.get_state()) == BookingState.confirming
        message.answer.assert_awaited_once_with(
            CONFIRMING_MESSAGE, reply_markup=build_remove_reply()
        )

    def test_non_text_comment_shows_error(
        self, message: AsyncMock, state: FSMContext
    ) -> None:
        asyncio.run(state.set_state(BookingState.entering_comment))
        asyncio.run(handle_non_text_comment(message))
        assert asyncio.run(state.get_state()) == BookingState.entering_comment
        message.answer.assert_awaited_once()


# ===================================================================
# Router registration — tests through actual dispatcher/routing
# ===================================================================


class TestRouter:
    def test_booking_router_is_registered_in_dispatcher(self) -> None:
        from bot.loader import create_dispatcher

        dispatcher = create_dispatcher()
        assert len(dispatcher.sub_routers) == 2

        booking_router = dispatcher.sub_routers[1]
        assert booking_router.name == "bot.handlers.booking"
        # 3 callback + 9 message handlers
        assert len(booking_router.callback_query.handlers) == 3
        # cancel (all states) + name/text + name/non-text + contact + phone/text
        # + phone/non-text + skip + comment/text + comment/non-text
        assert len(booking_router.message.handlers) == 9

    def test_dispatcher_can_be_created_multiple_times(self) -> None:
        from bot.loader import create_dispatcher

        d1 = create_dispatcher()
        d2 = create_dispatcher()
        assert len(d1.sub_routers) == 2
        assert len(d2.sub_routers) == 2

    def test_text_cancel_registered_before_name_input(self) -> None:
        """Cancel handler must be registered first so it takes priority."""
        from bot.loader import create_dispatcher

        dispatcher = create_dispatcher()
        booking_router = dispatcher.sub_routers[1]
        handlers = booking_router.message.handlers

        # First handler should be text cancel
        first = handlers[0]
        assert "text_cancel" in first.callback.__name__

    def test_cancel_has_state_filter(self) -> None:
        """Cancel handler's StateFilter covers entering_name, entering_phone, entering_comment."""
        from bot.loader import create_dispatcher

        dispatcher = create_dispatcher()
        booking_router = dispatcher.sub_routers[1]
        handlers = booking_router.message.handlers

        cancel_handler = handlers[0]
        # The first filter is a FilterObject wrapping StateFilter
        raw_filter = cancel_handler.filters[0].callback
        assert isinstance(raw_filter, StateFilter)
        state_keys = {s.state for s in raw_filter.states}
        assert "BookingState:entering_name" in state_keys
        assert "BookingState:entering_phone" in state_keys
        assert "BookingState:entering_comment" in state_keys

    def test_skip_comment_registered_before_text_comment(self) -> None:
        """Skip comment handler must be registered before generic text handler."""
        from bot.loader import create_dispatcher

        dispatcher = create_dispatcher()
        booking_router = dispatcher.sub_routers[1]
        handlers = booking_router.message.handlers

        # Find skip_comment and comment_input positions
        names = [h.callback.__name__ for h in handlers]
        skip_idx = names.index("handle_skip_comment")
        comment_idx = names.index("handle_comment_input")
        assert skip_idx < comment_idx, (
            f"skip at {skip_idx} must be before comment at {comment_idx}"
        )

    def test_contact_registered_before_phone_text(self) -> None:
        """Contact handler must be registered before phone text handler."""
        from bot.loader import create_dispatcher

        dispatcher = create_dispatcher()
        booking_router = dispatcher.sub_routers[1]
        handlers = booking_router.message.handlers

        names = [h.callback.__name__ for h in handlers]
        contact_idx = names.index("handle_contact")
        phone_text_idx = names.index("handle_phone_text")
        assert contact_idx < phone_text_idx, (
            f"contact at {contact_idx} must be before phone_text at {phone_text_idx}"
        )

    def test_non_text_name_registered_after_text_name(self) -> None:
        """Non-text fallback must be registered after text handler."""
        from bot.loader import create_dispatcher

        dispatcher = create_dispatcher()
        booking_router = dispatcher.sub_routers[1]
        handlers = booking_router.message.handlers

        names = [h.callback.__name__ for h in handlers]
        name_idx = names.index("handle_name_input")
        non_text_idx = names.index("handle_non_text_name")
        assert name_idx < non_text_idx
