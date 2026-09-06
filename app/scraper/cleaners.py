import re
from typing import Any, Optional


def extract_battery_mah(battery_str: Optional[str]) -> Optional[int]:
    if not battery_str:
        return None
    match = re.search(r"(\d{3,5})\s*mAh", battery_str, re.IGNORECASE)
    return int(match.group(1)) if match else None


def extract_display_size(display_str: Optional[str]) -> Optional[float]:
    if not display_str:
        return None
    match = re.search(r"(\d+(?:\.\d+)?)\s*inches", display_str, re.IGNORECASE)
    return float(match.group(1)) if match else None


def extract_weight_grams(weight_str: Optional[str]) -> Optional[float]:
    if not weight_str:
        return None
    match = re.search(r"(\d+(?:\.\d+)?)\s*g", weight_str, re.IGNORECASE)
    return float(match.group(1)) if match else None


def clean_text(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    cleaned = re.sub(r"\s+", " ", text).strip()
    return cleaned if cleaned else None


def clean_phone_record(record: dict[str, Any]) -> dict[str, Any]:
    """Normalize parsed phone fields before validation and persistence."""
    cleaned = dict(record)
    text_fields = {
        "model_name",
        "brand",
        "source_url",
        "image_url",
        "release_date",
        "dimensions",
        "os",
        "display_type",
        "resolution",
        "chipset",
        "cpu",
        "gpu",
        "storage_ram",
        "main_camera",
        "selfie_camera",
        "charging_speed",
        "price",
    }
    for field in text_fields:
        if field in cleaned:
            cleaned[field] = clean_text(cleaned[field])
    cleaned["raw_specs"] = {
        clean_text(category) or "General": {
            clean_text(key) or "Other": clean_text(value) or ""
            for key, value in values.items()
        }
        for category, values in (cleaned.get("raw_specs") or {}).items()
    }
    cleaned["weight_g"] = extract_weight_grams(cleaned.pop("weight_raw", None))
    cleaned["display_size_inches"] = extract_display_size(
        cleaned.pop("display_size_raw", None)
    )
    cleaned["battery_capacity_mah"] = extract_battery_mah(
        cleaned.pop("battery_raw", None)
    )
    cleaned["brand"] = cleaned.get("brand") or "Samsung"
    return cleaned