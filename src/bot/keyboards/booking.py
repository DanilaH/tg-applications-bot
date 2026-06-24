from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from bot.services.catalog import ALLOWED_SERVICES


def build_service_keyboard() -> InlineKeyboardMarkup:
    """Build an inline keyboard with one button per service plus a cancel button."""
    buttons: list[list[InlineKeyboardButton]] = []

    for service in ALLOWED_SERVICES:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=service.name,
                    callback_data=f"booking:service:{service.id}",
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text="Отмена",
                callback_data="booking:cancel",
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_name_keyboard() -> InlineKeyboardMarkup:
    """Build an inline keyboard with a cancel button for the name input step."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Отмена",
                    callback_data="booking:cancel",
                )
            ]
        ]
    )


def build_phone_keyboard() -> ReplyKeyboardMarkup:
    """Build a reply keyboard with a request-contact button and a cancel button."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Отправить телефон", request_contact=True),
            ],
            [
                KeyboardButton(text="Отмена"),
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def build_comment_keyboard() -> ReplyKeyboardMarkup:
    """Build a reply keyboard with skip and cancel buttons."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Пропустить"),
            ],
            [
                KeyboardButton(text="Отмена"),
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def build_remove_reply() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()
