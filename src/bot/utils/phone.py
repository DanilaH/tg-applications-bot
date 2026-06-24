import re


def normalize_phone(raw: str) -> str | None:
    """Normalise a phone number to 10–15 digits, preserving a leading '+' if present.

    Only one '+' is allowed, and it must be at the start.
    Returns the normalised string or None if the input is invalid.
    """
    cleaned = raw.strip()
    if not cleaned:
        return None

    # Allow only digits, spaces, +, (), -
    if not re.fullmatch(r"[0-9+\s()\-]+", cleaned):
        return None

    # At most one '+', and it must be at the start
    plus_count = cleaned.count("+")
    if plus_count > 1:
        return None
    if plus_count == 1 and not cleaned.startswith("+"):
        return None

    # Extract digits
    digits = re.sub(r"\D", "", cleaned)
    if len(digits) < 10 or len(digits) > 15:
        return None

    # Keep leading '+' if the original had one
    if cleaned.startswith("+"):
        return f"+{digits}"
    return digits
