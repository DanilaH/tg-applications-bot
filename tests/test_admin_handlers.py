import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.types import CallbackQuery, User

from bot.config import Settings
from bot.handlers.admin import handle_admin_booking_action
from bot.repositories.booking_repository import BookingRepositoryError


@pytest.fixture
def settings():
    return Settings(
        bot_token="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
        admin_chat_id=999,
        database_url="sqlite:///:memory:",
    )


def test_handle_admin_booking_action_unauthorized(settings):
    callback = AsyncMock(spec=CallbackQuery)
    callback.from_user = MagicMock(spec=User)
    callback.from_user.id = 111  # Not admin
    callback.data = "admin:booking:accept:1"
    callback.answer = AsyncMock()

    asyncio.run(handle_admin_booking_action(callback, settings))

    callback.answer.assert_called_once_with(
        "Это действие доступно только администратору.", show_alert=True
    )


def test_handle_admin_booking_action_accept_success(settings, monkeypatch):
    callback = AsyncMock(spec=CallbackQuery)
    callback.from_user = MagicMock(spec=User)
    callback.from_user.id = 999  # Admin
    callback.data = "admin:booking:accept:42"
    callback.message = AsyncMock()
    callback.answer = AsyncMock()

    mock_update = MagicMock(return_value=True)
    monkeypatch.setattr("bot.handlers.admin.update_booking_status", mock_update)

    asyncio.run(handle_admin_booking_action(callback, settings))

    mock_update.assert_called_once_with(
        database_url=settings.database_url,
        booking_id=42,
        status="accepted",
    )
    callback.message.edit_reply_markup.assert_called_once_with(reply_markup=None)
    callback.message.answer.assert_called_once_with("Заявка #42 принята.")
    callback.answer.assert_called_once()


def test_handle_admin_booking_action_decline_success(settings, monkeypatch):
    callback = AsyncMock(spec=CallbackQuery)
    callback.from_user = MagicMock(spec=User)
    callback.from_user.id = 999  # Admin
    callback.data = "admin:booking:decline:42"
    callback.message = AsyncMock()
    callback.answer = AsyncMock()

    mock_update = MagicMock(return_value=True)
    monkeypatch.setattr("bot.handlers.admin.update_booking_status", mock_update)

    asyncio.run(handle_admin_booking_action(callback, settings))

    mock_update.assert_called_once_with(
        database_url=settings.database_url,
        booking_id=42,
        status="declined",
    )
    callback.message.edit_reply_markup.assert_called_once_with(reply_markup=None)
    callback.message.answer.assert_called_once_with("Заявка #42 отклонена.")
    callback.answer.assert_called_once()


def test_handle_admin_booking_action_not_found(settings, monkeypatch):
    callback = AsyncMock(spec=CallbackQuery)
    callback.from_user = MagicMock(spec=User)
    callback.from_user.id = 999  # Admin
    callback.data = "admin:booking:accept:404"
    callback.answer = AsyncMock()

    mock_update = MagicMock(return_value=False)
    monkeypatch.setattr("bot.handlers.admin.update_booking_status", mock_update)

    asyncio.run(handle_admin_booking_action(callback, settings))

    callback.answer.assert_called_once_with("Заявка не найдена.", show_alert=True)


def test_handle_admin_booking_action_repository_error(settings, monkeypatch):
    callback = AsyncMock(spec=CallbackQuery)
    callback.from_user = MagicMock(spec=User)
    callback.from_user.id = 999  # Admin
    callback.data = "admin:booking:accept:42"
    callback.answer = AsyncMock()

    mock_update = MagicMock(side_effect=BookingRepositoryError("DB Error"))
    monkeypatch.setattr("bot.handlers.admin.update_booking_status", mock_update)

    asyncio.run(handle_admin_booking_action(callback, settings))

    callback.answer.assert_called_once_with("Не удалось обновить статус заявки.", show_alert=True)
