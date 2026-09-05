"""
Shared Normalizers Module
=========================
Normalizes price strings, Indian numerical formats (Lakhs, K, M), star ratings, and titles.
"""
import re
from typing import Optional, Any


class SharedNormalizer:
    # Common non-price rejection patterns
    REJECT_PATTERNS = [
        re.compile(r'/(\s*mo|\s*month)', re.IGNORECASE),
        re.compile(r'per\s+month', re.IGNORECASE),
        re.compile(r'emi\s+(?:starts?\s+at|from)', re.IGNORECASE),
        re.compile(r'no\s+cost\s+emi', re.IGNORECASE),
        re.compile(r'save\s+[\d,₹]+(?:\s+with\s+coupon)?', re.IGNORECASE),
        re.compile(r'coupon\s+(?:discount|offer|savings|applied)', re.IGNORECASE),
        re.compile(r'apply\s+(?:₹|rs\.?|inr)?\s*\d+\s+coupon', re.IGNORECASE),
        re.compile(r'buy\s+(?:at|for)\s+(?:₹|rs\.?|inr)?\s*[\d,]+', re.IGNORECASE),
        re.compile(r'effective\s+price', re.IGNORECASE),
        re.compile(r'bank\s+(?:offer|discount|savings)', re.IGNORECASE),
        re.compile(r'credit\s+card\s+offer', re.IGNORECASE),
        re.compile(r'debit\s+card\s+offer', re.IGNORECASE),
        re.compile(r'instant\s+discount', re.IGNORECASE),
        re.compile(r'cashback', re.IGNORECASE),
        re.compile(r'off\s+on\s+exchange', re.IGNORECASE),
        re.compile(r'exchange\s+(?:value|offer|discount)', re.IGNORECASE),
        re.compile(r'with\s+exchange', re.IGNORECASE),
        re.compile(r'delivery\s+(?:fee|charge)', re.IGNORECASE),
        re.compile(r'special\s+price\s+get\s+extra', re.IGNORECASE),
    ]

    GENERIC_NOISE_TITLES = [
        "amazon product page", "amazon.in", "flipkart.com", "online shopping", "myntra", "ajio", "nykaa",
        "404 not found", "access denied", "page not found", "buy products online at best price in india - all categories",
    ]

    TITLE_CLEAN_PATTERNS = [
        re.compile(r'\s*:\s*Buy\s+Online.*$', re.IGNORECASE),
        re.compile(r'\s*:\s*Amazon\.in.*$', re.IGNORECASE),
        re.compile(r'\s*Price\s+in\s+India\s*-\s*Buy.*$', re.IGNORECASE),
        re.compile(r'\s*Price\s+in\s+India.*$', re.IGNORECASE),
        re.compile(r'\s*-\s*Flipkart\.com.*$', re.IGNORECASE),
        re.compile(r'\s*\|\s*Flipkart.*$', re.IGNORECASE),
        re.compile(r'\s*-\s*Buy.*Online\s+at\s+Flipkart.*$', re.IGNORECASE),
        re.compile(r'\s*-\s*Buy.*Online\s+at\s+Myntra.*$', re.IGNORECASE),
        re.compile(r'\s*-\s*Buy.*Online\s+at\s+AJIO.*$', re.IGNORECASE),
        re.compile(r'\s*-\s*Nykaa.*$', re.IGNORECASE),
        re.compile(r'\s*\|\s*Nykaa.*$', re.IGNORECASE),
        re.compile(r'\s*-\s*Buy\s+.*Online.*$', re.IGNORECASE),
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
        if not text or text.startswith('-') or text.startswith('–'):
            return None

        # Check for rejection patterns
        for pattern in cls.REJECT_PATTERNS:
            if pattern.search(text):
                return None

        # Match digits with commas and optional decimals: ₹1,49,900.00
        match = re.search(r'(?:₹|rs\.?|inr)?\s*([\d,]+(?:\.\d{1,2})?)', text, re.IGNORECASE)
        if not match:
            return None

        num_str = match.group(1).replace(',', '')
        try:
            val = float(num_str)
            return val if val > 0 else None
        except (ValueError, TypeError):
            return None

    @classmethod
    def parse_rating(cls, raw: Optional[str | int | float]) -> Optional[float]:
        """
        Parse rating string to float between 0.0 and 5.0.
        """
        if raw is None:
            return None

        if isinstance(raw, (int, float)):
            val = float(raw)
            return round(val, 2) if 0.0 <= val <= 5.0 else None

        text = str(raw).strip()
        if not text or text.startswith('-') or text.startswith('–'):
            return None

        m = re.search(r'(\d+(?:\.\d+)?)', text)
        if m:
            try:
                val = float(m.group(1))
                if 0.0 <= val <= 5.0:
                    return round(val, 2)
                return None
            except (ValueError, TypeError):
                pass
        return None

    @classmethod
    def parse_count(cls, raw: Optional[str | int | float]) -> Optional[int]:
        """
        Parse rating count or review count strings supporting Indian formats.
        Examples: '1,48,271', '1.2 lakh', '2.5K', '10k', '1.5M', '(1,450 Reviews)'
        """
        if raw is None:
            return None

        if isinstance(raw, (int, float)):
            val = int(raw)
            return val if val >= 0 else None

        text = str(raw).strip().lower()
        if not text or text.startswith('-'):
            return None

        # Check for Lakh notation: '1.2 lakh', '15 lakhs'
        lakh_match = re.search(r'([\d,]+(?:\.\d+)?)\s*(?:lakh|lakhs|lac|lacs|l\b)', text)
        if lakh_match:
            try:
                num = float(lakh_match.group(1).replace(',', ''))
                return int(round(num * 100000))
            except ValueError:
                pass

        # Check for K notation (thousands): '15.4k', '2.5K'
        k_match = re.search(r'([\d,]+(?:\.\d+)?)\s*k\b', text)
        if k_match:
            try:
                num = float(k_match.group(1).replace(',', ''))
                return int(round(num * 1000))
            except ValueError:
                pass

        # Check for M notation (millions): '1.5M'
        m_match = re.search(r'([\d,]+(?:\.\d+)?)\s*m\b', text)
        if m_match:
            try:
                num = float(m_match.group(1).replace(',', ''))
                return int(round(num * 1000000))
            except ValueError:
                pass

        # Standard numbers: '1,48,271' or '24350'
        std_match = re.search(r'([\d,]+)', text)
        if std_match:
            try:
                clean = std_match.group(1).replace(',', '')
                return int(clean) if clean else None
            except ValueError:
                pass

        return None

    @classmethod
    def clean_title(cls, raw: Optional[str]) -> Optional[str]:
        """Clean raw product title by removing website noise and whitespace."""
        if not raw:
            return None
        text = " ".join(raw.split())
        for pattern in cls.TITLE_CLEAN_PATTERNS:
            text = pattern.sub('', text).strip()
        if text.lower() in cls.GENERIC_NOISE_TITLES or "buy products online at best price" in text.lower():
            return None
        return text if len(text) >= 3 else None
