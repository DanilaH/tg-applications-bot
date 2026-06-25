from aiogram import Bot


async def send_admin_notification(bot: Bot, admin_chat_id: int, text: str) -> None:
    """
    Sends a notification message to the administrator.
    No retries or queues as per requirements.
    """
    await bot.send_message(chat_id=admin_chat_id, text=text, parse_mode="HTML")
