from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def build_main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Записаться",
                    callback_data="booking:start",
                )
            ]
        ]
    )
