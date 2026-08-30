import json
from pathlib import Path

from app.database.connection import get_db, init_db
from app.database.crud import get_all_phones, upsert_phone
from app.scraper.scraper import GSMArenaScraper
from app.utils.logger import logger


def run_pipeline():
    logger.info("=== Starting Samsung Phone Scraper Pipeline ===")

    # 1. Initialize PostgreSQL schema
    init_db()

    # 2. Discover device URLs
    scraper = GSMArenaScraper()
    device_urls = scraper.get_target_device_urls()

    if not device_urls:
        logger.error("No device URLs found. Exiting pipeline.")
        return

    scraped_records = []

    # 3. Process each device
    for index, url in enumerate(device_urls, start=1):
        logger.info(
            f"[{index}/{len(device_urls)}] Scraping device specifications..."
        )
        data = scraper.scrape_device(url)

        if not data or not data.get("model_name"):
            logger.warning(f"Skipping incomplete record for URL: {url}")
            continue

        # Save to database
        with get_db() as db:
            upsert_phone(db, data)
            scraped_records.append(data)

    # 4. Save processed snapshot as local JSON
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "samsung_phones.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(scraped_records, f, indent=2, default=str)
    logger.info(f"Exported {len(scraped_records)} records to {output_path}")

    # 5. Database Summary Check
    with get_db() as db:
        total_in_db = len(get_all_phones(db))
        logger.info(
            f"=== Pipeline Finished. Total phones stored in PostgreSQL: {total_in_db} ==="
        )


if __name__ == "__main__":
    run_pipeline()