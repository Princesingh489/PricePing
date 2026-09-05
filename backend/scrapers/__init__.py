"""
Scrapers Package Entrypoint
"""
from db.models import PlatformEnum
from scrapers.base import BaseScraper
from scrapers.shared.models import (
    PriceCandidate,
    FieldConfidence,
    ExtractionDebug,
    ExtractionResult,
    AvailabilityEnum,
)
from scrapers.shared.normalizers import SharedNormalizer as PriceNormalizer
from scrapers.shared.normalizers import SharedNormalizer as NumberNormalizer
from scrapers.shared.confidence import ConfidenceEngine
from scrapers.amazon import AmazonScraper
from scrapers.flipkart import FlipkartScraper
from scrapers.myntra import MyntraScraper
from scrapers.ajio import AjioScraper
from scrapers.nykaa import NykaaScraper
from scrapers.scraper_router import (
    detect_platform_from_url,
    get_scraper_for_url,
    route_and_scrape,
    SCRAPER_REGISTRY,
)
from scrapers.playwright_manager import PlaywrightManager
from scrapers.playwright_pool import PlaywrightPool
from scrapers.cache import ScraperCache


def detect_store_platform(url: str) -> PlatformEnum:
    return detect_platform_from_url(url)


# Async alias helpers
async def scrape_amazon(url: str) -> ExtractionResult:
    return await AmazonScraper().extract_product(url)


async def scrape_flipkart(url: str) -> ExtractionResult:
    return await FlipkartScraper().extract_product(url)


async def scrape_myntra(url: str) -> ExtractionResult:
    return await MyntraScraper().extract_product(url)


async def scrape_ajio(url: str) -> ExtractionResult:
    return await AjioScraper().extract_product(url)


async def scrape_nykaa(url: str) -> ExtractionResult:
    return await NykaaScraper().extract_product(url)


__all__ = [
    "BaseScraper",
    "ExtractionResult",
    "ExtractionDebug",
    "PriceCandidate",
    "FieldConfidence",
    "PlatformEnum",
    "AvailabilityEnum",
    "AmazonScraper",
    "FlipkartScraper",
    "MyntraScraper",
    "AjioScraper",
    "NykaaScraper",
    "PlaywrightManager",
    "PlaywrightPool",
    "ScraperCache",
    "ConfidenceEngine",
    "PriceNormalizer",
    "NumberNormalizer",
    "detect_store_platform",
    "detect_platform_from_url",
    "get_scraper_for_url",
    "route_and_scrape",
    "scrape_amazon",
    "scrape_flipkart",
    "scrape_myntra",
    "scrape_nykaa",
    "scrape_ajio",
    "SCRAPER_REGISTRY",
]
