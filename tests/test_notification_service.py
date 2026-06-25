from unittest.mock import AsyncMock

from bot.services.notification_service import send_admin_notification


async def test_send_admin_notification_calls_bot_correctly() -> None:
    bot = AsyncMock()
    admin_chat_id = 12345
    text = "Hello Admin"

    await send_admin_notification(bot, admin_chat_id, text)

    bot.send_message.assert_awaited_once_with(
        chat_id=admin_chat_id,
        text=text,
        parse_mode="HTML"
    )
