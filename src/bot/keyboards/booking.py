from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

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
