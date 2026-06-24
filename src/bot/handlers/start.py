from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.keyboards.main_menu import build_main_menu

WELCOME_TEXT = (
    "Добро пожаловать! Здесь можно оставить заявку на запись в барбершоп. "
    "Нажмите кнопку ниже, чтобы начать."
)


async def handle_start(message: Message) -> None:
    await message.answer(WELCOME_TEXT, reply_markup=build_main_menu())


def create_start_router() -> Router:
    router = Router(name=__name__)
    router.message.register(handle_start, CommandStart())
    return router
