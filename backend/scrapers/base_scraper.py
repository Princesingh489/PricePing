"""
Base Scraper Module
===================
Abstract base class for all store-specific product scrapers.
Integrates modular extractors, validators, normalizers, and fail-closed confidence verification.
"""
import re
import json
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from bs4 import BeautifulSoup, Tag
from datetime import datetime

from db.models import PlatformEnum, AvailabilityEnum
from scrapers.normalizers import PriceNormalizer, NumberNormalizer
from scrapers.extractors import (
    JsonLdExtractor,
    MetaExtractor,
    DomExtractor,
    PriceExtractor,
    PriceCandidate,
    RatingExtractor,
    ImageExtractor,
)
from scrapers.validators import (
    PriceValidator,
    ProductValidator,
    ConfidenceValidator,
)

logger = logging.getLogger(__name__)


@dataclass
class ExtractionDebug:
    original_url: str
    normalized_url: str
    detected_store: str
    extracted_product_id: Optional[str] = None
    candidate_prices: List[Dict[str, Any]] = field(default_factory=list)
    extraction_sources: Dict[str, str] = field(default_factory=dict)
    confidence_score: int = 0
    status: str = "pending"
    warnings: List[str] = field(default_factory=list)


@dataclass
class ExtractionResult:
    store: PlatformEnum
    store_product_id: Optional[str]
    title: Optional[str] = None
    current_price: Optional[float] = None
    original_price: Optional[float] = None
    discount_percentage: Optional[float] = None
    image_url: Optional[str] = None
    rating: Optional[float] = None
    rating_count: Optional[int] = None
    review_count: Optional[int] = None
    currency: Optional[str] = "INR"
    availability: AvailabilityEnum = AvailabilityEnum.unknown
    description: Optional[str] = None
    confidence_score: int = 0
    status: str = "success"  # "success", "uncertain", "extraction_failed"
    extraction_sources: Dict[str, str] = field(default_factory=dict)
    debug_info: Optional[ExtractionDebug] = None
    success: bool = True
    error_message: Optional[str] = None
    product_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        store_val = self.store.value if hasattr(self.store, 'value') else str(self.store)
        return {
            "platform": store_val,
            "store": store_val,
            "store_product_id": self.store_product_id,
            "product_id": self.store_product_id,
            "title": self.title,
            "current_price": self.current_price,
            "price": self.current_price,
            "original_price": self.original_price,
            "discount_percentage": self.discount_percentage,
            "image": self.image_url,
            "product_image": self.image_url,
            "image_url": self.image_url,
            "rating": self.rating,
            "rating_count": self.rating_count,
            "review_count": self.review_count,
            "currency": self.currency or "INR",
            "availability": self.availability.value if hasattr(self.availability, 'value') else str(self.availability),
            "description": self.description,
            "confidence_score": self.confidence_score,
            "status": self.status,
            "success": self.success,
            "error": self.error_message,
            "error_message": self.error_message,
            "product_url": self.product_url,
            "url": self.product_url,
            "final_url": self.product_url,
            "extraction_sources": self.extraction_sources,
            "fetched_at": datetime.utcnow().isoformat() + "Z",
        }

    def __getitem__(self, key: str) -> Any:
        return self.to_dict()[key]

    def __contains__(self, key: str) -> bool:
        return key in self.to_dict()

    def get(self, key: str, default: Any = None) -> Any:
        return self.to_dict().get(key, default)


class BaseScraper(ABC):
    """
    Abstract base class for all store-specific product scrapers.
    """
    store: PlatformEnum = PlatformEnum.unknown

    normalize_flipkart_image = staticmethod(ImageExtractor.normalize_flipkart_image)
    extract_largest_from_srcset = staticmethod(ImageExtractor.extract_largest_from_srcset)

    @abstractmethod
    def extract_product_id(self, url: str) -> Optional[str]:
        """Extract store-specific unique product identifier."""
        raise NotImplementedError

    @abstractmethod
    def get_main_container(self, soup: BeautifulSoup) -> Optional[Tag]:
        """Identify and return the main product container element in the DOM."""
        raise NotImplementedError

    @abstractmethod
    async def extract_product(self, url: str) -> ExtractionResult:
        """Fetch and extract product data for the given URL."""
        raise NotImplementedError

    # -------------------------------------------------------------
    # Shared Normalization and Validation Helpers
    # -------------------------------------------------------------

    def parse_price(self, text: Any) -> Optional[float]:
        return PriceNormalizer.clean_price(text)

    def parse_rating(self, text: Any) -> Optional[float]:
        return NumberNormalizer.parse_rating(text)

    def parse_count(self, text: Any) -> Optional[int]:
        return NumberNormalizer.parse_count(text)

    def calculate_discount(self, current_price: Optional[float], original_price: Optional[float]) -> Optional[float]:
        if current_price is not None and original_price is not None and original_price > current_price > 0:
            return float(round(((original_price - current_price) / original_price) * 100))
        return None

    def clean_title(self, raw_title: Optional[str]) -> Optional[str]:
        return DomExtractor.clean_title(raw_title)

    def sanitize_image_url(self, raw_url: Optional[str], page_url: Optional[str] = None) -> Optional[str]:
        return ImageExtractor.sanitize_image_url(raw_url, page_url or "")

    def is_rejected_price_text(self, text: str) -> bool:
        return PriceNormalizer.clean_price(text) is None
