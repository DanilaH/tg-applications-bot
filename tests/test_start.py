import asyncio
from unittest.mock import AsyncMock

from bot.handlers.start import WELCOME_TEXT, handle_start
from bot.keyboards.main_menu import build_main_menu
from bot.loader import create_dispatcher


def test_main_menu_contains_booking_button() -> None:
    keyboard = build_main_menu()

    assert len(keyboard.inline_keyboard) == 1
    assert len(keyboard.inline_keyboard[0]) == 1

    button = keyboard.inline_keyboard[0][0]
    assert button.text == "Записаться"
    assert button.callback_data == "booking:start"


def test_start_handler_sends_welcome_message() -> None:
    message = AsyncMock()

    asyncio.run(handle_start(message))

    message.answer.assert_awaited_once_with(
        WELCOME_TEXT,
        reply_markup=build_main_menu(),
    )


def test_start_router_is_registered() -> None:
    from pydantic import SecretStr

    from bot.config import Settings
    settings = Settings(
        bot_token=SecretStr("123:abc"),
        admin_chat_id=98765,
        _env_file=None,
    )
    dispatcher = create_dispatcher(settings)

    assert len(dispatcher.sub_routers) >= 1
    start_router = dispatcher.sub_routers[0]
    assert start_router.name == "bot.handlers.start"
    assert len(start_router.message.handlers) == 1
