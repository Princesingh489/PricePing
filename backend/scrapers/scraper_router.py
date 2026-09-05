"""
Scraper Router Module
=====================
Detects e-commerce store platform from product URL and routes to the appropriate modular scraper.
"""
import re
import logging
from typing import Optional, Tuple
from db.models import PlatformEnum
from scrapers.base import BaseScraper
from scrapers.shared.models import ExtractionResult
from scrapers.amazon.scraper import AmazonScraper
from scrapers.flipkart.scraper import FlipkartScraper
from scrapers.myntra.scraper import MyntraScraper
from scrapers.ajio.scraper import AjioScraper
from scrapers.nykaa.scraper import NykaaScraper

logger = logging.getLogger(__name__)

# Platform registry
SCRAPER_REGISTRY = {
    PlatformEnum.amazon: AmazonScraper(),
    PlatformEnum.flipkart: FlipkartScraper(),
    PlatformEnum.myntra: MyntraScraper(),
    PlatformEnum.ajio: AjioScraper(),
    PlatformEnum.nykaa: NykaaScraper(),
}


def detect_platform_from_url(url: str) -> PlatformEnum:
    """Identify the e-commerce store platform from URL."""
    if not url:
        return PlatformEnum.unknown
    u = url.lower().strip()

    if "amazon.in" in u or "amzn.in" in u or "amzn.to" in u or "amazon.com" in u:
        return PlatformEnum.amazon
    elif "flipkart.com" in u or "dl.flipkart.com" in u or "fkrt.it" in u:
        return PlatformEnum.flipkart
    elif "myntra.com" in u:
        return PlatformEnum.myntra
    elif "ajio.com" in u or "ajio.in" in u or "ajio.page.link" in u:
        return PlatformEnum.ajio
    elif "nykaa.com" in u:
        return PlatformEnum.nykaa

    return PlatformEnum.unknown


def get_scraper_for_url(url: str) -> Tuple[Optional[BaseScraper], PlatformEnum]:
    """Retrieve scraper instance and detected platform for URL."""
    platform = detect_platform_from_url(url)
    scraper = SCRAPER_REGISTRY.get(platform)
    return scraper, platform


async def route_and_scrape(url: str) -> ExtractionResult:
    """Detect platform and execute adaptive extraction."""
    scraper, platform = get_scraper_for_url(url)
    if not scraper:
        return ExtractionResult(
            store=platform,
            store_product_id=None,
            status="uncertain",
            success=False,
            error_message=f"Unsupported e-commerce platform for URL: {url}",
            product_url=url,
        )
    return await scraper.extract_product(url)
