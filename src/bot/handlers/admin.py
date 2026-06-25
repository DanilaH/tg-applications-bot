import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.config import Settings
from bot.repositories.booking_repository import BookingRepositoryError, update_booking_status

logger = logging.getLogger(__name__)


async def handle_admin_booking_action(
    callback: CallbackQuery,
    settings: Settings,
) -> None:
    if callback.from_user.id != settings.admin_chat_id:
        await callback.answer("Это действие доступно только администратору.", show_alert=True)
        return

    data_parts = callback.data.split(":")
    if len(data_parts) != 4:
        return

    action = data_parts[2]  # accept or decline
    booking_id_str = data_parts[3]

    try:
        booking_id = int(booking_id_str)
    except ValueError:
        return

    status = "accepted" if action == "accept" else "declined"
    status_text = "принята" if action == "accept" else "отклонена"

    try:
        success = update_booking_status(
            database_url=settings.database_url,
            booking_id=booking_id,
            status=status,
        )
    except BookingRepositoryError:
        logger.error("Failed to update booking status for %s due to SQLite error", booking_id)
        await callback.answer("Не удалось обновить статус заявки.", show_alert=True)
        return

    if not success:
        await callback.answer("Заявка не найдена.", show_alert=True)
        return

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"Заявка #{booking_id} {status_text}.")
    await callback.answer()


def create_admin_router() -> Router:
    router = Router(name=__name__)

    router.callback_query.register(
        handle_admin_booking_action,
        F.data.startswith("admin:booking:accept:") | F.data.startswith("admin:booking:decline:"),
    )

    return router
