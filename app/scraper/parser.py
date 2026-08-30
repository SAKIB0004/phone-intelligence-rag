from typing import Any, Dict, List

from bs4 import BeautifulSoup

from app.scraper.cleaners import (
    clean_text,
    extract_battery_mah,
    extract_display_size,
    extract_weight_grams,
)


class GSMArenaParser:

    @staticmethod
    def parse_device_links(html_content: str, base_url: str) -> List[str]:
        """Extract individual device spec URLs from the catalog page."""
        soup = BeautifulSoup(html_content, "lxml")
        makers_div = soup.find("div", class_="makers")
        if not makers_div:
            return []

        links = []
        for a_tag in makers_div.find_all("a", href=True):
            href = a_tag["href"]
            full_url = (
                f"{base_url}/{href}" if not href.startswith("http") else href
            )
            links.append(full_url)
        return links

    @staticmethod
    def parse_phone_details(html_content: str, source_url: str) -> Dict[str, Any]:
        """Parse structured specification data from a device page."""
        soup = BeautifulSoup(html_content, "lxml")

        # 1. Model Name
        title_tag = soup.find("h1", class_="specs-phone-name-title")
        model_name = (
            clean_text(title_tag.text) if title_tag else "Unknown Model"
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
            category_name = (
                clean_text(category_th.text) if category_th else "General"
            )
            raw_specs[category_name] = {}

            rows = table.find_all("tr")
            for row in rows:
                ttl_td = row.find("td", class_="ttl")
                nfo_td = row.find("td", class_="nfo")
                if ttl_td and nfo_td:
                    key = clean_text(ttl_td.text) or "Other"
                    val = clean_text(nfo_td.text) or ""
                    raw_specs[category_name][key] = val
                    flat_specs[key.lower()] = val

        # 4. Map structured fields
        weight_raw = flat_specs.get("weight")
        display_raw = flat_specs.get("size")
        battery_raw = flat_specs.get("type", "") + " " + flat_specs.get("batdescription1", "")

        return {
            "model_name": model_name,
            "brand": "Samsung",
            "source_url": source_url,
            "image_url": image_url,
            "release_date": flat_specs.get("announced") or flat_specs.get("status"),
            "dimensions": flat_specs.get("dimensions"),
            "weight_g": extract_weight_grams(weight_raw),
            "os": flat_specs.get("os"),
            "display_type": flat_specs.get("type"),
            "display_size_inches": extract_display_size(display_raw),
            "resolution": flat_specs.get("resolution"),
            "chipset": flat_specs.get("chipset"),
            "cpu": flat_specs.get("cpu"),
            "gpu": flat_specs.get("gpu"),
            "storage_ram": flat_specs.get("internal"),
            "main_camera": flat_specs.get("triple") or flat_specs.get("dual") or flat_specs.get("single") or flat_specs.get("quad"),
            "selfie_camera": flat_specs.get("single") if "selfie" in str(raw_specs.get("Selfie camera", {})) else None,
            "battery_capacity_mah": extract_battery_mah(battery_raw),
            "charging_speed": flat_specs.get("charging"),
            "price": flat_specs.get("price"),
            "raw_specs": raw_specs,
        }