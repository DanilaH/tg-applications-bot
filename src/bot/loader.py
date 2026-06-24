from aiogram import Bot, Dispatcher

from bot.config import Settings
from bot.handlers.booking import create_booking_router
from bot.handlers.start import create_start_router


def create_bot(settings: Settings) -> Bot:
    return Bot(token=settings.bot_token.get_secret_value())


def create_dispatcher() -> Dispatcher:
    dispatcher = Dispatcher()
    dispatcher.include_router(create_start_router())
    dispatcher.include_router(create_booking_router())
    return dispatcher
