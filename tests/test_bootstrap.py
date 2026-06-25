import asyncio
from unittest.mock import AsyncMock

from aiogram import Bot, Dispatcher
from pydantic import SecretStr

from bot import loader, main
from bot.config import Settings


def test_loader_creates_telegram_components_without_network() -> None:
    settings = Settings(
        bot_token=SecretStr("123456:TEST_TOKEN"),
        admin_chat_id=987654321,
        _env_file=None,
    )

    bot = loader.create_bot(settings)
    dispatcher = loader.create_dispatcher(settings)

    assert isinstance(bot, Bot)
    assert isinstance(dispatcher, Dispatcher)
    assert dispatcher["settings"] == settings
    asyncio.run(bot.session.close())


def test_run_starts_polling_without_network(monkeypatch) -> None:
    settings = Settings(
        bot_token=SecretStr("123456:TEST_TOKEN"),
        admin_chat_id=987654321,
        _env_file=None,
    )
    bot = loader.create_bot(settings)
    dispatcher = loader.create_dispatcher(settings)
    start_polling = AsyncMock()
    close_session = AsyncMock()
    monkeypatch.setattr(main, "get_settings", lambda: settings)
    monkeypatch.setattr(main, "create_bot", lambda _: bot)
    monkeypatch.setattr(main, "create_dispatcher", lambda _: dispatcher)
    monkeypatch.setattr(dispatcher, "start_polling", start_polling)
    monkeypatch.setattr(bot.session, "close", close_session)

    asyncio.run(main.run())

    start_polling.assert_awaited_once_with(bot)
    close_session.assert_awaited_once_with()
