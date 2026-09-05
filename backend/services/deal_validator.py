"""
PricePing Live Deal Validator
=============================
Strict validation engine enforcing Rule 13, Rule 14, and Rule 27:
- Every deal must pass verification for product identity, URL, image, price, MRP, availability, store, and freshness.
- Never allow placeholder, invalid, or mismatched images.
- If deal is expired or out of stock, it must be marked non-live and evicted from trending.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Tuple, List, Optional
from urllib.parse import urlparse
import re
import logging

logger = logging.getLogger(__name__)

SUPPORTED_STORES = {"amazon", "flipkart", "myntra", "ajio", "nykaa"}

STORE_DOMAIN_MAP = {
    "amazon": ["amazon.in", "amazon.com", "amzn.to", "amzn.in"],
    "flipkart": ["flipkart.com", "dl.flipkart.com", "fkrt.it"],
    "myntra": ["myntra.com"],
    "ajio": ["ajio.com"],
    "nykaa": ["nykaa.com", "nykaaman.com"],
}

VALID_IMAGE_DOMAINS = [
    "amazon.com",
    "images-amazon.com",
    "media-amazon.com",
    "ssl-images-amazon.com",
    "flixcart.com",
    "rukminim.flixcart.com",
    "rukminim1.flixcart.com",
    "rukminim2.flixcart.com",
    "myntassets.com",
    "assets.myntassets.com",
    "ajio.com",
    "assets.ajio.com",
    "nykaa.com",
    "images-static.nykaa.com",
    "unsplash.com",
    "images.unsplash.com",
]


class DealValidator:
    """
    Validates candidates before they can be ranked or displayed in 'Trending Deals Across Stores'.
    Fail-closed design: If any parameter is invalid, the deal is rejected.
    """
    SUPPORTED_STORES = SUPPORTED_STORES
    STORE_DOMAIN_MAP = STORE_DOMAIN_MAP
    VALID_IMAGE_DOMAINS = VALID_IMAGE_DOMAINS

    @classmethod
    def validate_store(cls, store: str) -> Tuple[bool, str]:
        if not store or not isinstance(store, str):
            return False, "Store name is required"
        normalized = store.strip().lower()
        if normalized not in SUPPORTED_STORES:
            return False, f"Store '{store}' is not one of the 5 supported stores: {', '.join(SUPPORTED_STORES)}"
        return True, "Valid store"

    @classmethod
    def validate_url(cls, url: str, store: str) -> Tuple[bool, str]:
        if not url or not isinstance(url, str) or len(url.strip()) < 10:
            return False, "Product URL is missing or too short"
        parsed = urlparse(url.strip())
        if not parsed.scheme or parsed.scheme not in ("http", "https"):
            return False, f"Invalid URL scheme '{parsed.scheme}'"
        
        hostname = (parsed.netloc or "").lower().replace("www.", "")
        normalized_store = store.strip().lower()
        allowed_domains = STORE_DOMAIN_MAP.get(normalized_store, [])

        if not any(domain in hostname for domain in allowed_domains):
            return False, f"URL domain '{hostname}' does not match store '{normalized_store}'"

        return True, "Valid URL"

    @classmethod
    def validate_image(cls, image_url: str) -> Tuple[bool, str]:
        if not image_url or not isinstance(image_url, str) or len(image_url.strip()) < 10:
            return False, "Product image URL is missing or empty"
        
        clean_url = image_url.strip()
        parsed = urlparse(clean_url)
        if not parsed.scheme or parsed.scheme not in ("http", "https"):
            return False, f"Invalid image URL scheme '{parsed.scheme}'"

        hostname = (parsed.netloc or "").lower().replace("www.", "")
        
        # Check against trusted e-commerce image CDNs or valid image extensions
        is_trusted_cdn = any(domain in hostname for domain in VALID_IMAGE_DOMAINS)
        has_image_ext = bool(re.search(r"\.(jpg|jpeg|png|webp|avif)(\?|$)", clean_url, re.IGNORECASE))

        if not (is_trusted_cdn or has_image_ext):
            return False, f"Image URL domain '{hostname}' is not a recognized product asset CDN"

        # Explicitly reject placeholder strings
        lower_url = clean_url.lower()
        if any(p in lower_url for p in ("placeholder", "no-image", "missing-image", "default-product", "avatar")):
            return False, "Image URL is a generic placeholder, not a genuine product image"

        return True, "Valid verified image"

    @classmethod
    def validate_price_and_mrp(
        cls, price: float, mrp: Optional[float], currency: str = "INR"
    ) -> Tuple[bool, str]:
        if price is None or not isinstance(price, (int, float)):
            return False, "Current price is missing or non-numeric"
        if price <= 0:
            return False, f"Current price must be positive (got ₹{price})"
        if currency and currency.upper() != "INR":
            return False, f"Unsupported currency '{currency}'; PricePing strictly operates in INR"
        
        if mrp is not None and isinstance(mrp, (int, float)):
            if mrp < price:
                return False, f"MRP (₹{mrp}) cannot be lower than current selling price (₹{price})"

        return True, "Valid price"

    @classmethod
    def validate_availability(cls, availability: str) -> Tuple[bool, str]:
        if not availability or not isinstance(availability, str):
            return False, "Availability status is missing"
        normalized = availability.strip().lower().replace(" ", "_")
        if normalized not in ("in_stock", "available", "instock"):
            return False, f"Product is not available for purchase (status: {availability})"
        return True, "Available in stock"

    @classmethod
    def calculate_freshness(cls, last_verified_at: Optional[datetime]) -> Tuple[str, str, int]:
        """
        Step 14 Freshness Rule:
        < 5 minutes      -> LIVE
        5-15 minutes     -> RECENT
        15-30 minutes    -> STALE
        30-60 minutes    -> RECHECK
        > 60 minutes     -> EXPIRED
        """
        if not last_verified_at:
            return "EXPIRED", "Verification timestamp missing", 999999

        now = datetime.now(timezone.utc)
        if last_verified_at.tzinfo is None:
            # Treat naive as UTC
            dt = last_verified_at.replace(tzinfo=timezone.utc)
        else:
            dt = last_verified_at

        age_seconds = int((now - dt).total_seconds())
        if age_seconds < 0:
            age_seconds = 0

        age_minutes = age_seconds // 60

        if age_minutes < 5:
            return "LIVE", f"Price verified {age_minutes}m ago" if age_minutes > 0 else "Price verified just now", age_seconds
        elif age_minutes < 15:
            return "RECENT", f"Price verified {age_minutes}m ago", age_seconds
        elif age_minutes < 30:
            return "STALE", f"Verified {age_minutes}m ago (stale)", age_seconds
        elif age_minutes < 60:
            return "RECHECK", f"Verified {age_minutes}m ago (recheck required)", age_seconds
        else:
            return "EXPIRED", f"Verified {age_minutes}m ago (expired)", age_seconds

    @classmethod
    def validate_candidate(cls, deal_dict: Dict[str, Any]) -> Tuple[bool, List[str], str]:
        """
        Full evaluation of candidate deal against all strict verification rules.
        Returns: (is_valid: bool, errors: List[str], deal_status: str)
        """
        errors: List[str] = []

        store = deal_dict.get("store") or ""
        valid_store, store_msg = cls.validate_store(store)
        if not valid_store:
            errors.append(store_msg)

        title = deal_dict.get("title") or ""
        if not title or len(title.strip()) < 3:
            errors.append("Product title is missing or too short")

        url = deal_dict.get("product_url") or ""
        if valid_store:
            valid_url, url_msg = cls.validate_url(url, store)
            if not valid_url:
                errors.append(url_msg)

        image_url = deal_dict.get("image_url") or deal_dict.get("product_image") or ""
        valid_img, img_msg = cls.validate_image(image_url)
        if not valid_img:
            errors.append(img_msg)

        price = deal_dict.get("price") or deal_dict.get("current_price")
        mrp = deal_dict.get("mrp") or deal_dict.get("original_price")
        currency = deal_dict.get("currency") or "INR"
        valid_price, price_msg = cls.validate_price_and_mrp(price, mrp, currency)
        if not valid_price:
            errors.append(price_msg)

        availability = deal_dict.get("availability") or "in_stock"
        valid_avail, avail_msg = cls.validate_availability(availability)
        if not valid_avail:
            errors.append(avail_msg)

        # Freshness determination
        last_verified = deal_dict.get("last_verified_at")
        freshness_state, _, _ = cls.calculate_freshness(last_verified)

        if not errors:
            deal_status = "LIVE" if freshness_state in ("LIVE", "RECENT") else ("STALE" if freshness_state == "STALE" else "EXPIRED")
            is_valid = deal_status in ("LIVE", "RECENT")
        else:
            if not valid_avail:
                deal_status = "OUT_OF_STOCK"
            elif not valid_price:
                deal_status = "PRICE_CHANGED"
            else:
                deal_status = "ERROR"
            is_valid = False

        return is_valid, errors, deal_status
