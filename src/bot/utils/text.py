from collections.abc import Mapping
from html import escape


def _required_text(data: Mapping[str, object], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Missing booking field: {key}")
    return value.strip()


def format_booking_summary(data: Mapping[str, object]) -> str:
    service_name = escape(_required_text(data, "service_name"))
    customer_name = escape(_required_text(data, "customer_name"))
    phone = escape(_required_text(data, "phone"))

    comment_value = data.get("comment")
    if comment_value is None:
        comment = "Не указан"
    elif isinstance(comment_value, str) and comment_value.strip():
        comment = escape(comment_value.strip())
    else:
        raise ValueError("Invalid booking field: comment")

    return (
        "<b>Проверьте заявку</b>\n\n"
        f"<b>Услуга:</b> {service_name}\n"
        f"<b>Имя:</b> {customer_name}\n"
        f"<b>Телефон:</b> {phone}\n"
        f"<b>Комментарий:</b> {comment}"
    )
