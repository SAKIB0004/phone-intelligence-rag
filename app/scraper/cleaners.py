import re
from typing import Optional


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