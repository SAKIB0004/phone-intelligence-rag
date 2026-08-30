import random
import time
from typing import Dict, List, Optional
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config.settings import settings
from app.scraper.parser import GSMArenaParser
from app.utils.logger import logger


class GSMArenaScraper:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": settings.USER_AGENT,
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Referer": "https://www.google.com/",
            }
        )

    def _respectful_sleep(self) -> None:
        delay = random.uniform(
            settings.REQUEST_DELAY_MIN, settings.REQUEST_DELAY_MAX
        )
        time.sleep(delay)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=3, max=10),
        reraise=True,
    )
    def fetch_page(self, url: str) -> str:
        """Fetch HTML content with automatic retries and error handling."""
        logger.info(f"Fetching URL: {url}")
        self._respectful_sleep()
        response = self.session.get(url, timeout=15)

        if response.status_code == 429:
            logger.warning("Rate limit hit (429). Backing off...")
            time.sleep(10)
            response.raise_for_status()

        response.raise_for_status()
        return response.text

    def get_target_device_urls(
        self, limit: int = settings.TARGET_PHONE_COUNT
    ) -> List[str]:
        """Fetch list of Samsung phone links from the brand catalog."""
        catalog_html = self.fetch_page(settings.SAMSUNG_PAGE_URL)
        device_links = GSMArenaParser.parse_device_links(
            catalog_html, settings.BASE_URL
        )
        logger.info(
            f"Found {len(device_links)} device URLs. Limiting to {limit}."
        )
        return device_links[:limit]

    def scrape_device(self, url: str) -> Optional[Dict]:
        """Fetch and parse a single device page."""
        try:
            html = self.fetch_page(url)
            return GSMArenaParser.parse_phone_details(html, url)
        except Exception as e:
            logger.error(f"Failed to scrape device at {url}: {e}")
            return None