import pytest
from pydantic import ValidationError

from bot.config import Settings


def test_settings_load_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "123456:TEST_TOKEN")
    monkeypatch.setenv("ADMIN_CHAT_ID", "987654321")

    settings = Settings(_env_file=None)

    assert settings.bot_token.get_secret_value() == "123456:TEST_TOKEN"
    assert settings.admin_chat_id == 987654321


def test_settings_require_bot_token_and_admin_chat_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("BOT_TOKEN", raising=False)
    monkeypatch.delenv("ADMIN_CHAT_ID", raising=False)

    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None)

    error_text = str(exc_info.value)
    assert "bot_token" in error_text
    assert "admin_chat_id" in error_text


def test_settings_do_not_reveal_bot_token(monkeypatch: pytest.MonkeyPatch) -> None:
    token = "123456:VERY_SECRET_TOKEN"
    monkeypatch.setenv("BOT_TOKEN", token)
    monkeypatch.setenv("ADMIN_CHAT_ID", "987654321")

    settings = Settings(_env_file=None)

    assert token not in str(settings)
    assert token not in repr(settings)
