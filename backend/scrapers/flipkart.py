"""
Flipkart Scraper (Compatibility Wrapper)
"""
from scrapers.flipkart.scraper import FlipkartScraper

async def scrape_flipkart(url: str):
    return await FlipkartScraper().extract_product(url)

__all__ = ["FlipkartScraper", "scrape_flipkart"]

