from typing import Any
from urllib.parse import urlparse


REQUIRED_FIELDS = ("model_name", "brand", "source_url")


def validate_phone_record(record: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate the cleaned phone record before database persistence."""
    errors: list[str] = []

    for field in REQUIRED_FIELDS:
        if not record.get(field):
            errors.append(f"missing {field}")

    if record.get("brand") and record["brand"].lower() != "samsung":
        errors.append("brand must be Samsung")

    source_url = record.get("source_url")
    if source_url:
        parsed_url = urlparse(source_url)
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            errors.append("source_url must be an absolute HTTP(S) URL")

    numeric_fields = {
        "weight_g": (0, 1000),
        "display_size_inches": (0, 20),
        "battery_capacity_mah": (0, 20000),
    }
    for field, (minimum, maximum) in numeric_fields.items():
        value = record.get(field)
        if value is not None and not minimum <= value <= maximum:
            errors.append(f"{field} is outside the valid range")

    return not errors, errors
