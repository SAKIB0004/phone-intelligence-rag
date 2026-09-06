from typing import Any, Dict, List

from bs4 import BeautifulSoup

class GSMArenaParser:

    @staticmethod
    def parse_phone_details(html_content: str, source_url: str) -> Dict[str, Any]:
        """Parse structured specification data from a device page."""
        soup = BeautifulSoup(html_content, "lxml")

        # 1. Model Name
        title_tag = soup.find("h1", class_="specs-phone-name-title")
        model_name = (
            title_tag.get_text() if title_tag else None
        )

        # 2. Image URL
        img_div = soup.find("div", class_="specs-photo-main")
        image_url = None
        if img_div and img_div.find("img"):
            image_url = img_div.find("img").get("src")

        # 3. Extract All Spec Tables
        raw_specs: Dict[str, Dict[str, str]] = {}
        flat_specs: Dict[str, str] = {}

        tables = soup.find_all("table", cellspacing="0")
        for table in tables:
            category_th = table.find("th")
            category_name = category_th.get_text() if category_th else "General"
            raw_specs[category_name] = {}

            rows = table.find_all("tr")
            for row in rows:
                ttl_td = row.find("td", class_="ttl")
                nfo_td = row.find("td", class_="nfo")
                if ttl_td and nfo_td:
                    key = ttl_td.get_text()
                    val = nfo_td.get_text()
                    raw_specs[category_name][key] = val
                    flat_specs[key.strip().lower()] = val

        def category_value(category: str, key: str) -> str | None:
            values = next(
                (
                    values
                    for name, values in raw_specs.items()
                    if name.strip().lower() == category.lower()
                ),
                {},
            )
            return next(
                (
                    value
                    for name, value in values.items()
                    if name.strip().lower() == key
                ),
                None,
            )

        display_type = category_value("Display", "type") or flat_specs.get("type")
        battery_raw = " ".join(
            value
            for value in (
                category_value("Battery", "type"),
                category_value("Battery", "batdescription1"),
            )
            if value
        )

        return {
            "model_name": model_name,
            "brand": "Samsung",
            "source_url": source_url,
            "image_url": image_url,
            "release_date": flat_specs.get("announced") or flat_specs.get("status"),
            "dimensions": flat_specs.get("dimensions"),
            "weight_raw": flat_specs.get("weight"),
            "os": flat_specs.get("os"),
            "display_type": display_type,
            "display_size_raw": flat_specs.get("size"),
            "resolution": flat_specs.get("resolution"),
            "chipset": flat_specs.get("chipset"),
            "cpu": flat_specs.get("cpu"),
            "gpu": flat_specs.get("gpu"),
            "storage_ram": flat_specs.get("internal"),
            "main_camera": flat_specs.get("triple") or flat_specs.get("dual") or flat_specs.get("single") or flat_specs.get("quad"),
            "selfie_camera": flat_specs.get("single") if "selfie" in str(raw_specs.get("Selfie camera", {})) else None,
            "battery_raw": battery_raw,
            "charging_speed": flat_specs.get("charging"),
            "price": flat_specs.get("price"),
            "raw_specs": raw_specs,
        }