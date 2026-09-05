"""
JSON-LD Structured Data Extractor
=================================
Extracts schema.org Product schemas, offers, ratings, and image metadata from <script type="application/ld+json">.
"""
import json
import logging
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from scrapers.normalizers.price_normalizer import PriceNormalizer
from scrapers.normalizers.number_normalizer import NumberNormalizer

logger = logging.getLogger(__name__)


class JsonLdExtractor:
    @classmethod
    def extract_all(cls, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract all JSON-LD product dictionaries from the page."""
        results = []
        for script in soup.find_all("script", type="application/ld+json"):
            if not script.string:
                continue
            try:
                data = json.loads(script.string.strip())
                if isinstance(data, dict):
                    if data.get("@type") == "Product" or "Product" in str(data.get("@type")):
                        results.append(data)
                    elif "@graph" in data and isinstance(data["@graph"], list):
                        for item in data["@graph"]:
                            if isinstance(item, dict) and (item.get("@type") == "Product" or "Product" in str(item.get("@type"))):
                                results.append(item)
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and (item.get("@type") == "Product" or "Product" in str(item.get("@type"))):
                            results.append(item)
            except Exception:
                continue
        return results

    @classmethod
    def extract_product_data(cls, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract structured product fields from JSON-LD."""
        items = cls.extract_all(soup)
        if not items:
            return {}

        primary = items[0]
        title = primary.get("name")
        description = primary.get("description")
        image = None
        current_price = None
        original_price = None
        currency = "INR"
        rating = None
        rating_count = None
        review_count = None

        # Images
        raw_img = primary.get("image")
        if isinstance(raw_img, str):
            image = raw_img
        elif isinstance(raw_img, list) and len(raw_img) > 0:
            image = raw_img[0]
        elif isinstance(raw_img, dict) and "url" in raw_img:
            image = raw_img["url"]

        # Offers
        offers = primary.get("offers")
        if isinstance(offers, dict):
            current_price = PriceNormalizer.clean_price(offers.get("price") or offers.get("lowPrice"))
            original_price = PriceNormalizer.clean_price(offers.get("highPrice"))
            currency = offers.get("priceCurrency") or "INR"
        elif isinstance(offers, list) and len(offers) > 0:
            first_offer = offers[0]
            if isinstance(first_offer, dict):
                current_price = PriceNormalizer.clean_price(first_offer.get("price") or first_offer.get("lowPrice"))
                original_price = PriceNormalizer.clean_price(first_offer.get("highPrice"))
                currency = first_offer.get("priceCurrency") or "INR"

        if not original_price and "hasVariant" in primary and isinstance(primary["hasVariant"], list):
            for v in primary["hasVariant"]:
                if isinstance(v, dict) and isinstance(v.get("offers"), dict) and v["offers"].get("highPrice"):
                    original_price = PriceNormalizer.clean_price(v["offers"]["highPrice"])
                    break

        # Ratings
        agg = primary.get("aggregateRating")
        if isinstance(agg, dict):
            rating = NumberNormalizer.parse_rating(agg.get("ratingValue"))
            rating_count = NumberNormalizer.parse_count(agg.get("ratingCount") or agg.get("reviewCount"))
            review_count = NumberNormalizer.parse_count(agg.get("reviewCount"))

        return {
            "title": title,
            "description": description,
            "image": image,
            "current_price": current_price,
            "original_price": original_price,
            "currency": currency,
            "rating": rating,
            "rating_count": rating_count,
            "review_count": review_count,
        }
