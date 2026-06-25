import pytest

from bot.utils.text import format_admin_booking_message, format_booking_summary


def test_format_booking_summary_with_comment() -> None:
    summary = format_booking_summary(
        {
            "service_name": "Стрижка + борода",
            "customer_name": "Иван",
            "phone": "+79991234567",
            "comment": "После 18:00",
        }
    )

    assert summary == (
        "<b>Проверьте заявку</b>\n\n"
        "<b>Услуга:</b> Стрижка + борода\n"
        "<b>Имя:</b> Иван\n"
        "<b>Телефон:</b> +79991234567\n"
        "<b>Комментарий:</b> После 18:00"
    )


def test_format_booking_summary_without_comment() -> None:
    summary = format_booking_summary(
        {
            "service_name": "Консультация",
            "customer_name": "Анна",
            "phone": "1234567890",
            "comment": None,
        }
    )

    assert "<b>Комментарий:</b> Не указан" in summary


def test_format_booking_summary_escapes_dynamic_values() -> None:
    summary = format_booking_summary(
        {
            "service_name": "Стрижка & уход",
            "customer_name": '<Иван "Тест">',
            "phone": "+1234567890",
            "comment": "Хочу <вечером> & без очереди",
        }
    )

    assert "Стрижка &amp; уход" in summary
    assert "&lt;Иван &quot;Тест&quot;&gt;" in summary
    assert "Хочу &lt;вечером&gt; &amp; без очереди" in summary


@pytest.mark.parametrize("missing_key", ["service_name", "customer_name", "phone"])
def test_format_booking_summary_requires_complete_data(missing_key: str) -> None:
    data = {
        "service_name": "Консультация",
        "customer_name": "Анна",
        "phone": "1234567890",
        "comment": None,
    }
    del data[missing_key]

    with pytest.raises(ValueError):
        format_booking_summary(data)


def test_format_admin_booking_message_full_data() -> None:
    data = {
        "service_name": "Стрижка",
        "customer_name": "Иван",
        "phone": "+79991234567",
        "comment": "Тест",
    }
    msg = format_admin_booking_message(
        data=data,
        user_id=123,
        username="ivan_test",
        created_at_utc="2024-01-01 12:00:00",
        booking_id=42,
    )

    assert "<b>Новая заявка</b>" in msg
    assert "<b>Услуга:</b> Стрижка" in msg
    assert "<b>Имя:</b> Иван" in msg
    assert "<b>Телефон:</b> +79991234567" in msg
    assert "<b>Комментарий:</b> Тест" in msg
    assert "<b>Telegram ID:</b> <code>123</code>" in msg
    assert "<b>Username:</b> @ivan_test" in msg
    assert "<b>Создана (UTC):</b> 2024-01-01 12:00:00" in msg


def test_format_admin_booking_message_no_comment_no_username() -> None:
    data = {
        "service_name": "Консультация",
        "customer_name": "Анна",
        "phone": "1234567890",
        "comment": None,
    }
    msg = format_admin_booking_message(
        data=data,
        user_id=456,
        username=None,
        created_at_utc="2024-02-02 10:00:00",
    )

    assert "<b>Комментарий:</b> Не указан" in msg
    assert "<b>Username:</b> Не указан" in msg


def test_format_admin_booking_message_escapes_html() -> None:
    data = {
        "service_name": "<b>Bold</b>",
        "customer_name": "<i>Italic</i>",
        "phone": "+123",
        "comment": "&",
    }
    msg = format_admin_booking_message(
        data=data,
        user_id=789,
        username="<bad>",
        created_at_utc="2024-03-03 15:00:00",
    )

    assert "&lt;b&gt;Bold&lt;/b&gt;" in msg
    assert "&lt;i&gt;Italic&lt;/i&gt;" in msg
    assert "<b>Комментарий:</b> &amp;" in msg
    assert "<b>Username:</b> @&lt;bad&gt;" in msg


def test_format_admin_booking_message_incomplete_data_raises_value_error() -> None:
    data = {"service_name": "Test"}
    with pytest.raises(ValueError):
        format_admin_booking_message(data, 1, None, "now")
