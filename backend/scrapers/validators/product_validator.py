"""
Product Coherence and Metadata Validator
========================================
Validates overall product data integrity, title validity, image health, and field sanity.
"""
from typing import Optional, Dict, Any


class ProductValidator:
    @classmethod
    def validate_title(cls, title: Optional[str]) -> bool:
        """Ensure title is non-empty, not generic noise, and reasonable length."""
        if not title:
            return False
        clean = title.strip()
        if len(clean) < 3 or len(clean) > 500:
            return False
        # Reject generic non-product titles
        noise_titles = ["amazon.in", "flipkart.com", "online shopping", "myntra", "ajio", "nykaa", "404 not found", "access denied"]
        if clean.lower() in noise_titles:
            return False
        return True

    @classmethod
    def validate_image(cls, image_url: Optional[str]) -> bool:
        """Ensure image URL is well-formed HTTP/HTTPS URL and non-placeholder."""
        if not image_url:
            return False
        url = image_url.strip().lower()
        if not (url.startswith("http://") or url.startswith("https://")):
            return False
        if any(bad in url for bad in ["spacer.gif", "1x1", "placeholder", "logo"]):
            return False
        return True

    @classmethod
    def validate_rating(cls, rating: Optional[float]) -> bool:
        """Ensure rating is between 0.0 and 5.0."""
        if rating is None:
            return True
        return 0.0 <= rating <= 5.0
