import random
import time

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

    def _respectful_sleep(self):
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

    def get_target_device_urls(self):
        """Return the explicitly selected Samsung smartphone URLs."""

        target_phone_urls = [
            # Galaxy S Series
            "https://www.gsmarena.com/samsung_galaxy_s21-10626.php",
            "https://www.gsmarena.com/samsung_galaxy_s22-11253.php",
            "https://www.gsmarena.com/samsung_galaxy_s23-12082.php",
            "https://www.gsmarena.com/samsung_galaxy_s24-12773.php",
            "https://www.gsmarena.com/samsung_galaxy_s25-12827.php",

            # Galaxy S26 Series
            "https://www.gsmarena.com/samsung_galaxy_s26_5g-14456.php",
            "https://www.gsmarena.com/samsung_galaxy_s26+_5g-14457.php",
            "https://www.gsmarena.com/samsung_galaxy_s26_ultra_5g-14320.php",

            # Galaxy A Series
            "https://www.gsmarena.com/samsung_galaxy_a27_5g-14606.php",
            "https://www.gsmarena.com/samsung_galaxy_a37_5g-14378.php",
            "https://www.gsmarena.com/samsung_galaxy_a57_5g-14379.php",

            # Galaxy M Series
            "https://www.gsmarena.com/samsung_galaxy_m17_5g-14221.php",
            "https://www.gsmarena.com/samsung_galaxy_m47_5g-14749.php",

            # Galaxy Z Series
            "https://www.gsmarena.com/samsung_galaxy_z_flip8_5g-14803.php",
            "https://www.gsmarena.com/samsung_galaxy_z_fold8_ultra_5g-14802.php",
        ]

        logger.info(
            f"Selected {len(target_phone_urls)} target Samsung smartphones."
        )

        for index, url in enumerate(target_phone_urls, start=1):
            logger.info(f"[{index}/{len(target_phone_urls)}] Target URL: {url}")

        return target_phone_urls

    def scrape_device(self, url: str):
        """Fetch and parse a single device page."""
        try:
            html = self.fetch_page(url)
            return GSMArenaParser.parse_phone_details(html, url)
        except requests.RequestException as e:
            logger.error(f"Failed to scrape device at {url}: {e}")
            return None