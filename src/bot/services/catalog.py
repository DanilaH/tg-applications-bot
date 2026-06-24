from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Service:
    """A single service with an identifier and display name."""

    id: str
    name: str


ALLOWED_SERVICES: tuple[Service, ...] = (
    Service("men_haircut", "Мужская стрижка"),
    Service("beard_trim", "Борода и контур"),
    Service("combo", "Стрижка + борода"),
    Service("consultation", "Консультация"),
)

ALLOWED_SERVICE_IDS: tuple[str, ...] = tuple(s.id for s in ALLOWED_SERVICES)

SERVICE_LOOKUP: dict[str, str] = {s.id: s.name for s in ALLOWED_SERVICES}


def get_service(service_id: str) -> Service | None:
    """Return a Service for the given id, or None if not found."""
    name = SERVICE_LOOKUP.get(service_id)
    if name is None:
        return None
    return Service(service_id, name)
