"""
Meta & OpenGraph Extractor Module
=================================
Extracts OpenGraph, Twitter Card, and HTML meta tags.
"""
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
from scrapers.normalizers.price_normalizer import PriceNormalizer


class MetaExtractor:
    @classmethod
    def extract_metadata(cls, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract metadata tags from HTML head."""
        data = {}

        # Title
        og_title = soup.find("meta", property="og:title") or soup.find("meta", attrs={"name": "title"}) or soup.find("meta", attrs={"name": "twitter:title"})
        if og_title and og_title.get("content"):
            data["title"] = og_title["content"].strip()
        elif soup.title and soup.title.string:
            data["title"] = soup.title.string.strip()

        # Image
        og_image = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "twitter:image"}) or soup.find("meta", property="og:image:secure_url")
        if og_image and og_image.get("content"):
            data["image"] = og_image["content"].strip()

        # Price
        og_price = (
            soup.find("meta", property="og:price:amount") or
            soup.find("meta", property="product:price:amount") or
            soup.find("meta", attrs={"name": "twitter:data1"})
        )
        if og_price and og_price.get("content"):
            data["price"] = PriceNormalizer.clean_price(og_price["content"])

        # Currency
        og_currency = (
            soup.find("meta", property="og:price:currency") or
            soup.find("meta", property="product:price:currency")
        )
        if og_currency and og_currency.get("content"):
            data["currency"] = og_currency["content"].strip()

        # Description
        og_desc = soup.find("meta", property="og:description") or soup.find("meta", attrs={"name": "description"})
        if og_desc and og_desc.get("content"):
            data["description"] = og_desc["content"].strip()

        return data
