"""
Price Normalizer Module
=======================
Sanitizes raw price strings, handles Indian numbering format, and filters out non-product prices (EMI, coupons, cashback).
"""
import re
from typing import Optional


class PriceNormalizer:
    # Common non-price rejection patterns
    REJECT_PATTERNS = [
        re.compile(r'/(\s*mo|\s*month)', re.IGNORECASE),
        re.compile(r'per\s+month', re.IGNORECASE),
        re.compile(r'emi\s+(?:starts?\s+at|from)', re.IGNORECASE),
        re.compile(r'save\s+[\d,₹]+(?:\s+with\s+coupon)?', re.IGNORECASE),
        re.compile(r'coupon\s+(?:discount|offer)', re.IGNORECASE),
        re.compile(r'cashback', re.IGNORECASE),
        re.compile(r'off\s+on\s+exchange', re.IGNORECASE),
        re.compile(r'exchange\s+value', re.IGNORECASE),
        re.compile(r'delivery\s+(?:fee|charge)', re.IGNORECASE),
        re.compile(r'no\s+cost\s+emi', re.IGNORECASE),
    ]

    @classmethod
    def clean_price(cls, raw: Optional[str | int | float]) -> Optional[float]:
        """
        Extract numeric float from price string.
        Rejects EMI, coupon, and invalid price patterns.
        """
        if raw is None:
            return None

        if isinstance(raw, (int, float)):
            val = float(raw)
            return val if val > 0 else None

        text = str(raw).strip()
        if not text:
            return None

        # Reject negative numbers
        if text.startswith('-') or text.startswith('–'):
            return None

        # Check for rejection patterns
        for pattern in cls.REJECT_PATTERNS:
            if pattern.search(text):
                return None

        # Remove currency symbols, whitespace, and irrelevant text
        # Match standard prices like: ₹1,49,900.00, Rs. 1,299, 15999, 899.00
        # Match digits with optional commas and decimal point
        match = re.search(r'(?:₹|rs\.?|inr)?\s*([\d,]+(?:\.\d{1,2})?)', text, re.IGNORECASE)
        if not match:
            return None

        num_str = match.group(1).replace(',', '')
        try:
            val = float(num_str)
            return val if val > 0 else None
        except (ValueError, TypeError):
            return None
