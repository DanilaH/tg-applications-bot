from aiogram import Bot, Dispatcher

from bot.config import Settings
from bot.handlers.admin import create_admin_router
from bot.handlers.booking import create_booking_router
from bot.handlers.start import create_start_router


def create_bot(settings: Settings) -> Bot:
    return Bot(token=settings.bot_token.get_secret_value())


def create_dispatcher(settings: Settings | None = None) -> Dispatcher:
    dispatcher = Dispatcher()
    if settings:
        dispatcher["settings"] = settings
    dispatcher.include_router(create_start_router())
    dispatcher.include_router(create_admin_router())
    dispatcher.include_router(create_booking_router())
    return dispatcher
