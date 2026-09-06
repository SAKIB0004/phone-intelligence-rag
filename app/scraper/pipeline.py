import json
from pathlib import Path

from app.database.connection import get_db, init_db
from app.database.crud import get_all_phones, upsert_phone
from app.rag.retriever import SamsungRAGRetriever
from app.scraper.cleaners import clean_phone_record
from app.scraper.scraper import GSMArenaScraper
from app.scraper.validator import validate_phone_record
from app.utils.logger import logger


def run_pipeline():
	logger.info("=== Starting Samsung Phone Scraper Pipeline ===")
	init_db()
	scraper = GSMArenaScraper()
	device_urls = scraper.get_target_device_urls()
	scraped_records = []

	for index, url in enumerate(device_urls, start=1):
		logger.info(f"[{index}/{len(device_urls)}] Scraping device specifications...")
		data = scraper.scrape_device(url)
		if not data:
			logger.warning(f"Skipping failed scrape for URL: {url}")
			continue
		cleaned_record = clean_phone_record(data)
		is_valid, errors = validate_phone_record(cleaned_record)
		if not is_valid:
			logger.warning(f"Skipping invalid record for {url}: {', '.join(errors)}")
			continue
		with get_db() as db:
			upsert_phone(db, cleaned_record)
		scraped_records.append(cleaned_record)

	output_path = Path("data/processed/samsung_phones.json")
	output_path.parent.mkdir(parents=True, exist_ok=True)
	output_path.write_text(json.dumps(scraped_records, indent=2, default=str), encoding="utf-8")

	with get_db() as db:
		total_in_db = len(get_all_phones(db))
	indexed_count = SamsungRAGRetriever().index_database()
	logger.info(f"=== Pipeline finished. Total phones stored: {total_in_db} ===")
	return {
		"scraped_count": len(scraped_records),
		"total_phones": total_in_db,
		"indexed_phones": indexed_count,
		"output_path": str(output_path),
	}
