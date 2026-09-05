"""
Number Normalizer Module
========================
Parses and normalizes ratings and counts (supporting Indian notation like Lakhs, K, M).
"""
import re
from typing import Optional


class NumberNormalizer:
    @classmethod
    def parse_rating(cls, raw: Optional[str | int | float]) -> Optional[float]:
        """
        Parse rating string to float between 0.0 and 5.0.
        Examples: '4.2 ★', '4.5 out of 5 stars', '3.9 / 5', '4.8'
        """
        if raw is None:
            return None

        if isinstance(raw, (int, float)):
            val = float(raw)
            return round(val, 2) if 0.0 <= val <= 5.0 else None

        text = str(raw).strip()
        if not text or text.startswith('-') or text.startswith('–'):
            return None

        # Look for pattern: single decimal/integer rating number
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
        Parse counts handling Indian format, lakhs, k, m suffixes.
        Examples: '1,48,271', '1.2 lakh', '2.5K', '10K', '1.5M', '(1,450 Reviews)'
        """
        if raw is None:
            return None

        if isinstance(raw, int):
            return raw if raw >= 0 else None

        if isinstance(raw, float):
            return int(raw) if raw >= 0 else None

        text = str(raw).strip().lower()
        if not text:
            return None

        # Lakh / Lac notation (e.g. 1.2 lakh -> 120,000)
        m_lakh = re.search(r'([\d,]+(?:\.\d+)?)\s*(?:lakhs?|lacs?|l\b)', text)
        if m_lakh:
            try:
                num = float(m_lakh.group(1).replace(',', ''))
                return int(num * 100000)
            except Exception:
                pass

        # K (Thousands) notation (e.g. 2.5k -> 2,500)
        m_k = re.search(r'([\d,]+(?:\.\d+)?)\s*k\b', text)
        if m_k:
            try:
                num = float(m_k.group(1).replace(',', ''))
                return int(num * 1000)
            except Exception:
                pass

        # M (Millions) notation (e.g. 1.5m -> 1,500,000)
        m_m = re.search(r'([\d,]+(?:\.\d+)?)\s*m\b', text)
        if m_m:
            try:
                num = float(m_m.group(1).replace(',', ''))
                return int(num * 1000000)
            except Exception:
                pass

        # Standard Indian comma-separated or integer digits: '1,48,271' or '59'
        m_std = re.search(r'([\d,]+)', text)
        if m_std:
            try:
                cleaned = m_std.group(1).replace(',', '')
                val = int(cleaned)
                return val if val >= 0 else None
            except Exception:
                pass

        return None
