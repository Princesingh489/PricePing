"""
Router (Compatibility Wrapper)
"""
from scrapers.scraper_router import (
    detect_platform_from_url,
    get_scraper_for_url,
    route_and_scrape,
    SCRAPER_REGISTRY,
)

__all__ = [
    "detect_platform_from_url",
    "get_scraper_for_url",
    "route_and_scrape",
    "SCRAPER_REGISTRY",
]
