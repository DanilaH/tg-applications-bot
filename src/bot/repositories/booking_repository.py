import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class BookingCreate:
    service_id: str
    service_name: str
    customer_name: str
    phone: str
    comment: str | None
    telegram_user_id: int
    telegram_username: str | None
    created_at_utc: str


class BookingRepositoryError(RuntimeError):
    pass


def _database_path(database_url: str) -> str:
    prefix = "sqlite:///"
    if not database_url.startswith(prefix):
        raise BookingRepositoryError("Only sqlite:/// database URLs are supported")

    path = database_url[len(prefix) :]
    if not path:
        raise BookingRepositoryError("SQLite database path is empty")

    return path


def _connect(database_url: str) -> sqlite3.Connection:
    path = _database_path(database_url)
    if path != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)

    try:
        return sqlite3.connect(path)
    except sqlite3.Error as exc:
        raise BookingRepositoryError("Could not connect to SQLite database") from exc


def init_database(database_url: str) -> None:
    try:
        with _connect(database_url) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_id TEXT NOT NULL,
                    service_name TEXT NOT NULL,
                    customer_name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    comment TEXT,
                    telegram_user_id INTEGER NOT NULL,
                    telegram_username TEXT,
                    status TEXT NOT NULL DEFAULT 'new',
                    created_at_utc TEXT NOT NULL
                )
                """
            )
    except sqlite3.Error as exc:
        raise BookingRepositoryError("Could not initialize SQLite database") from exc


def create_booking(database_url: str, booking: BookingCreate) -> int:
    try:
        with _connect(database_url) as connection:
            cursor = connection.execute(
                """
                INSERT INTO bookings (
                    service_id,
                    service_name,
                    customer_name,
                    phone,
                    comment,
                    telegram_user_id,
                    telegram_username,
                    status,
                    created_at_utc
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 'new', ?)
                """,
                (
                    booking.service_id,
                    booking.service_name,
                    booking.customer_name,
                    booking.phone,
                    booking.comment,
                    booking.telegram_user_id,
                    booking.telegram_username,
                    booking.created_at_utc,
                ),
            )
            booking_id = cursor.lastrowid
    except sqlite3.Error as exc:
        raise BookingRepositoryError("Could not save booking") from exc

    if booking_id is None:
        raise BookingRepositoryError("SQLite did not return a booking id")

    return booking_id
