from aiogram import Bot, Dispatcher

from bot.config import Settings


def create_bot(settings: Settings) -> Bot:
    return Bot(token=settings.bot_token.get_secret_value())


def create_dispatcher() -> Dispatcher:
    return Dispatcher()
