import datetime
import logging
import re

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ContentType, Message

from bot.config import Settings
from bot.keyboards.booking import (
    build_admin_booking_keyboard,
    build_comment_keyboard,
    build_confirmation_keyboard,
    build_name_keyboard,
    build_phone_keyboard,
    build_remove_reply,
    build_service_keyboard,
)
from bot.keyboards.main_menu import build_main_menu
from bot.repositories.booking_repository import (
    BookingCreate,
    BookingRepositoryError,
    create_booking,
)
from bot.services.catalog import get_service
from bot.services.notification_service import send_admin_notification
from bot.states.booking import BookingState
from bot.utils.phone import normalize_phone
from bot.utils.text import format_admin_booking_message, format_booking_summary

logger = logging.getLogger(__name__)

SERVICE_PROMPT = "Выберите услугу:"
NAME_PROMPT_TEMPLATE = "Вы выбрали: {service_name}\n\nТеперь введите ваше имя:"
PHONE_PROMPT = "Введите номер телефона или нажмите кнопку «Отправить телефон»:"
COMMENT_PROMPT = "Добавьте комментарий к заявке или нажмите «Пропустить» (до 500 символов):"
CONFIRMING_MESSAGE = "Данные собраны."
READY_TO_SUBMIT_MESSAGE = "Заявка подтверждена и готова к отправке."
INCOMPLETE_BOOKING_MESSAGE = "Не удалось собрать заявку. Пожалуйста, начните заново."
NON_TEXT_ERROR = "Пожалуйста, отправьте текст."
EMPTY_COMMENT_ERROR = "Комментарий пустой. Напишите текст или нажмите «Пропустить»."
CANCEL_MESSAGE = "Запись отменена."
BOOKING_STORAGE_ERROR_MESSAGE = "Не удалось сохранить заявку. Пожалуйста, попробуйте ещё раз позже."
BOOKING_NOTIFICATION_ERROR_MESSAGE = (
    "Произошла ошибка при отправке заявки. Пожалуйста, попробуйте ещё раз позже."
)
BOOKING_SUCCESS_MESSAGE = "Заявка отправлена. Администратор скоро свяжется с вами."


def _normalize_name(raw: str) -> str | None:
    cleaned = re.sub(r"\s+", " ", raw.strip())
    if len(cleaned) < 2 or len(cleaned) > 80:
        return None
    return cleaned


async def _show_booking_summary(message: Message, state: FSMContext) -> None:
    data = await state.get_data()

    try:
        summary = format_booking_summary(data)
    except ValueError:
        await state.clear()
        from bot.handlers.start import WELCOME_TEXT

        await message.answer(
            INCOMPLETE_BOOKING_MESSAGE,
            reply_markup=build_remove_reply(),
        )
        await message.answer(
            WELCOME_TEXT,
            reply_markup=build_main_menu(),
        )
        return

    await state.set_state(BookingState.confirming)
    await message.answer(CONFIRMING_MESSAGE, reply_markup=build_remove_reply())
    await message.answer(
        summary,
        reply_markup=build_confirmation_keyboard(),
        parse_mode="HTML",
    )


async def handle_booking_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(BookingState.choosing_service)
    await callback.message.edit_text(
        SERVICE_PROMPT,
        reply_markup=build_service_keyboard(),
    )
    await callback.answer()


async def handle_service_selection(callback: CallbackQuery, state: FSMContext) -> None:
    service_id = callback.data.removeprefix("booking:service:")
    service = get_service(service_id)

    if service is None:
        await callback.answer("Эта услуга недоступна", show_alert=True)
        return

    await state.update_data(service_id=service.id, service_name=service.name)
    await state.set_state(BookingState.entering_name)
    await callback.message.edit_text(
        NAME_PROMPT_TEMPLATE.format(service_name=service.name),
        reply_markup=build_name_keyboard(),
    )
    await callback.answer()


async def handle_inline_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    from bot.handlers.start import WELCOME_TEXT

    await callback.message.edit_text(
        WELCOME_TEXT,
        reply_markup=build_main_menu(),
    )
    await callback.answer()


def _utc_timestamp() -> str:
    return datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S")


def _required_booking_text(data: dict[str, object], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Missing booking field: {key}")
    return value.strip()


def _booking_comment(data: dict[str, object]) -> str | None:
    value = data.get("comment")
    if value is None:
        return None
    if isinstance(value, str) and value.strip():
        return value.strip()
    raise ValueError("Invalid booking field: comment")


def _existing_booking_id(data: dict[str, object]) -> int | None:
    value = data.get("booking_id")
    if isinstance(value, int) and value > 0:
        return value
    return None


def _build_booking_create(
    data: dict[str, object],
    user_id: int,
    username: str | None,
    created_at_utc: str,
) -> BookingCreate:
    return BookingCreate(
        service_id=_required_booking_text(data, "service_id"),
        service_name=_required_booking_text(data, "service_name"),
        customer_name=_required_booking_text(data, "customer_name"),
        phone=_required_booking_text(data, "phone"),
        comment=_booking_comment(data),
        telegram_user_id=user_id,
        telegram_username=username,
        created_at_utc=created_at_utc,
    )


async def handle_booking_confirm(
    callback: CallbackQuery,
    state: FSMContext,
    bot: Bot,
    settings: Settings,
) -> None:
    data = await state.get_data()
    user = callback.from_user
    user_id = int(user.id)
    username = user.username

    try:
        booking_id = _existing_booking_id(data)
        created_at_value = data.get("booking_created_at_utc")
        created_at = created_at_value if isinstance(created_at_value, str) else _utc_timestamp()

        if booking_id is None:
            booking = _build_booking_create(
                data=data,
                user_id=user_id,
                username=username,
                created_at_utc=created_at,
            )
            booking_id = create_booking(settings.database_url, booking)
            await state.update_data(
                booking_id=booking_id,
                booking_created_at_utc=created_at,
            )

        admin_text = format_admin_booking_message(
            data=data,
            user_id=user_id,
            username=username,
            created_at_utc=created_at,
            booking_id=booking_id,
        )
    except ValueError:
        await state.clear()
        from bot.handlers.start import WELCOME_TEXT

        await callback.message.answer(
            INCOMPLETE_BOOKING_MESSAGE,
            reply_markup=build_remove_reply(),
        )
        await callback.message.answer(
            WELCOME_TEXT,
            reply_markup=build_main_menu(),
        )
        await callback.answer()
        return
    except BookingRepositoryError:
        logger.error("Failed to save booking due to SQLite error")
        await callback.message.answer(BOOKING_STORAGE_ERROR_MESSAGE)
        await callback.answer()
        return

    try:
        await send_admin_notification(
            bot=bot,
            admin_chat_id=settings.admin_chat_id,
            text=admin_text,
            reply_markup=build_admin_booking_keyboard(booking_id),
        )
    except TelegramAPIError:
        logger.error("Failed to send admin notification due to Telegram API error")
        await callback.message.answer(BOOKING_NOTIFICATION_ERROR_MESSAGE)
        await callback.answer()
        return

    await state.clear()
    from bot.handlers.start import WELCOME_TEXT

    await callback.message.edit_text(
        BOOKING_SUCCESS_MESSAGE,
        reply_markup=None,
    )
    await callback.message.answer(
        WELCOME_TEXT,
        reply_markup=build_main_menu(),
    )
    await callback.answer()


async def handle_booking_restart(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(BookingState.choosing_service)
    await callback.message.edit_text(
        SERVICE_PROMPT,
        reply_markup=build_service_keyboard(),
    )
    await callback.answer()


async def handle_text_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    from bot.handlers.start import WELCOME_TEXT

    await message.answer(CANCEL_MESSAGE, reply_markup=build_remove_reply())
    await message.answer(
        WELCOME_TEXT,
        reply_markup=build_main_menu(),
    )


async def handle_name_input(message: Message, state: FSMContext) -> None:
    if message.text is None:
        await message.answer(NON_TEXT_ERROR)
        return

    name = _normalize_name(message.text)
    if name is None:
        await message.answer("Имя должно содержать от 2 до 80 символов. Попробуйте ещё раз.")
        return

    await state.update_data(customer_name=name)
    await state.set_state(BookingState.entering_phone)
    await message.answer(PHONE_PROMPT, reply_markup=build_phone_keyboard())


async def handle_phone_text(message: Message, state: FSMContext) -> None:
    if message.text is None:
        await message.answer("Пожалуйста, введите номер телефона текстом.")
        return

    phone = normalize_phone(message.text)
    if phone is None:
        await message.answer(
            "Некорректный номер телефона. Введите номер в международном формате "
            "(например, +7 999 123 45 67)."
        )
        return

    await state.update_data(phone=phone)
    await state.set_state(BookingState.entering_comment)
    await message.answer(COMMENT_PROMPT, reply_markup=build_comment_keyboard())


async def handle_contact(message: Message, state: FSMContext) -> None:
    contact = message.contact
    if contact is None:
        return

    if contact.user_id != message.from_user.id:
        await message.answer(
            "Вы можете отправить только свой номер телефона. "
            "Пожалуйста, нажмите «Отправить телефон» ещё раз.",
            reply_markup=build_phone_keyboard(),
        )
        return

    phone = normalize_phone(contact.phone_number)
    if phone is None:
        await message.answer(
            "Не удалось обработать номер из контакта. Пожалуйста, введите номер вручную.",
            reply_markup=build_phone_keyboard(),
        )
        return

    await state.update_data(phone=phone)
    await state.set_state(BookingState.entering_comment)
    await message.answer(COMMENT_PROMPT, reply_markup=build_comment_keyboard())


async def handle_comment_input(message: Message, state: FSMContext) -> None:
    if message.text is None:
        await message.answer("Пожалуйста, введите комментарий текстом.")
        return

    text = message.text.strip()
    if not text:
        await message.answer(EMPTY_COMMENT_ERROR)
        return

    if len(text) > 500:
        await message.answer("Комментарий слишком длинный. Пожалуйста, сократите до 500 символов.")
        return

    await state.update_data(comment=text)
    await _show_booking_summary(message, state)


async def handle_skip_comment(message: Message, state: FSMContext) -> None:
    await state.update_data(comment=None)
    await _show_booking_summary(message, state)


async def handle_non_text_name(message: Message) -> None:
    await message.answer(NON_TEXT_ERROR)


async def handle_non_text_phone(message: Message) -> None:
    await message.answer(
        "Пожалуйста, отправьте номер текстом или через кнопку «Отправить телефон»."
    )


async def handle_non_text_comment(message: Message) -> None:
    await message.answer("Пожалуйста, отправьте комментарий текстом.")


def create_booking_router() -> Router:
    router = Router(name=__name__)

    router.callback_query.register(
        handle_booking_start,
        F.data == "booking:start",
    )
    router.callback_query.register(
        handle_service_selection,
        StateFilter(BookingState.choosing_service),
        F.data.startswith("booking:service:"),
    )
    router.callback_query.register(
        handle_inline_cancel,
        StateFilter(
            BookingState.choosing_service,
            BookingState.entering_name,
            BookingState.entering_phone,
            BookingState.entering_comment,
            BookingState.confirming,
        ),
        F.data == "booking:cancel",
    )
    router.callback_query.register(
        handle_booking_confirm,
        StateFilter(BookingState.confirming),
        F.data == "booking:confirm",
    )
    router.callback_query.register(
        handle_booking_restart,
        StateFilter(BookingState.confirming),
        F.data == "booking:restart",
    )

    router.message.register(
        handle_text_cancel,
        StateFilter(
            BookingState.entering_name,
            BookingState.entering_phone,
            BookingState.entering_comment,
        ),
        F.text == "Отмена",
    )
    router.message.register(
        handle_name_input,
        StateFilter(BookingState.entering_name),
        F.text,
    )
    router.message.register(
        handle_non_text_name,
        StateFilter(BookingState.entering_name),
    )
    router.message.register(
        handle_contact,
        StateFilter(BookingState.entering_phone),
        F.content_type == ContentType.CONTACT,
    )
    router.message.register(
        handle_phone_text,
        StateFilter(BookingState.entering_phone),
        F.text,
    )
    router.message.register(
        handle_non_text_phone,
        StateFilter(BookingState.entering_phone),
    )
    router.message.register(
        handle_skip_comment,
        StateFilter(BookingState.entering_comment),
        F.text == "Пропустить",
    )
    router.message.register(
        handle_comment_input,
        StateFilter(BookingState.entering_comment),
        F.text,
    )
    router.message.register(
        handle_non_text_comment,
        StateFilter(BookingState.entering_comment),
    )

    return router
