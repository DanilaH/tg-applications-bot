from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup


async def send_admin_notification(
    bot: Bot,
    admin_chat_id: int,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    """
    Sends a notification message to the administrator.
    No retries or queues as per requirements.
    """
    await bot.send_message(
        chat_id=admin_chat_id,
        text=text,
        parse_mode="HTML",
        reply_markup=reply_markup,
    )
