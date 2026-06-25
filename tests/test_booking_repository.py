import sqlite3

import pytest

from bot.repositories.booking_repository import (
    BookingCreate,
    BookingRepositoryError,
    create_booking,
    init_database,
)


def _database_url(tmp_path) -> str:
    return f"sqlite:///{(tmp_path / 'bookings.sqlite3').as_posix()}"


def _booking() -> BookingCreate:
    return BookingCreate(
        service_id="combo",
        service_name="Стрижка + борода",
        customer_name="Иван",
        phone="+79991234567",
        comment=None,
        telegram_user_id=123,
        telegram_username="ivan",
        created_at_utc="2026-06-25 12:00:00",
    )


def test_init_database_is_idempotent(tmp_path) -> None:
    database_url = _database_url(tmp_path)

    init_database(database_url)
    init_database(database_url)

    db_path = tmp_path / "bookings.sqlite3"
    with sqlite3.connect(db_path) as connection:
        table_count = connection.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type = 'table' AND name = 'bookings'"
        ).fetchone()[0]

    assert table_count == 1


def test_create_booking_returns_id_and_persists_row(tmp_path) -> None:
    database_url = _database_url(tmp_path)
    init_database(database_url)

    booking_id = create_booking(database_url, _booking())

    db_path = tmp_path / "bookings.sqlite3"
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone()

    assert booking_id == 1
    assert row["service_id"] == "combo"
    assert row["service_name"] == "Стрижка + борода"
    assert row["customer_name"] == "Иван"
    assert row["phone"] == "+79991234567"
    assert row["comment"] is None
    assert row["telegram_user_id"] == 123
    assert row["telegram_username"] == "ivan"
    assert row["status"] == "new"
    assert row["created_at_utc"] == "2026-06-25 12:00:00"


def test_invalid_database_url_raises_repository_error() -> None:
    with pytest.raises(BookingRepositoryError):
        init_database("postgresql://localhost/bookings")
