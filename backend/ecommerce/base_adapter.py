"""
Base Ecommerce Store Adapter Interface
======================================
Abstract base class defining standardized capabilities for all e-commerce store adapters.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List


class BaseEcommerceAdapter(ABC):
    store_name: str = "unknown"
    display_name: str = "Unknown Store"
    logo_icon: str = "store"

    @abstractmethod
    def detect_url(self, url: str) -> bool:
        """Return True if this adapter handles the given product URL."""
        raise NotImplementedError

    @abstractmethod
    def extract_product_id(self, url: str) -> Optional[str]:
        """Extract store-specific product ID / SKU / ASIN from URL."""
        raise NotImplementedError

    @abstractmethod
    async def fetch_product(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Fetch full product details:
        {
            "store": str,
            "product_id": str,
            "title": str,
            "price": float,
            "original_price": Optional[float],
            "discount_percentage": Optional[float],
            "currency": str,
            "availability": str,
            "image_url": str,
            "images": List[str],
            "rating": Optional[float],
            "rating_count": Optional[int],
            "review_count": Optional[int],
            "brand": Optional[str],
            "seller": Optional[str],
            "url": str,
        }
        """
        raise NotImplementedError

    @abstractmethod
    async def fetch_current_price(self, url: str) -> Optional[float]:
        """Fetch latest verified current price."""
        raise NotImplementedError

    @abstractmethod
    async def search_matching_product(
        self,
        title: str,
        brand: Optional[str] = None,
        model: Optional[str] = None,
        variant: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Search store for the same product. Must verify exact identity and variant.
        Returns offer dictionary or None if unavailable/unmatched:
        {
            "store": str,
            "seller_name": str,
            "price": float,
            "original_price": Optional[float],
            "shipping_price": float,
            "delivery_text": str,
            "url": str,
            "availability": str,
            "external_product_id": str,
            "is_verified_match": bool,
        }
        """
        raise NotImplementedError
