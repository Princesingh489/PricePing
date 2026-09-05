"""
Historical Price Aggregator Service (Free Public Time-Series Ingestion)
========================================================================
Queries public e-commerce price history aggregation backends (PriceBefore, PriceHistory, Highcharts endpoints)
to retrieve up to 2 years of free historical price curves for Amazon, Flipkart, AJIO, Myntra, and Nykaa.
Includes millisecond timestamp conversion, spike/drop anomaly filtering, and daily minimum downsampling.
"""

from __future__ import annotations
import re
import json
import logging
from datetime import datetime, timezone, date
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import quote_plus, urlparse, parse_qs
import httpx

logger = logging.getLogger(__name__)

DESKTOP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/128.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json,*/*;q=0.8",
    "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    "Sec-Ch-Ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "DNT": "1",
}

# Regex to capture Highcharts time-series data array: [[1672531199000, 1499.0], ...]
HIGHCHARTS_DATA_REGEX = re.compile(
    r'data:\s*(\[\[\d+,\s*[\d\.]+\](?:,\s*\[\d+,\s*[\d\.]+\])*\])',
    re.MULTILINE
)

# Alternate regex matching series data or JSON array inside script tags
SERIES_SERIES_REGEX = re.compile(
    r'(?:series|points|history)\s*:\s*(\[\[\d+,\s*[\d\.]+\](?:,\s*\[\d+,\s*[\d\.]+\])*\])',
    re.IGNORECASE | re.MULTILINE
)


class HistoricalAggregatorService:
    """
    Public price history time-series extractor with resilient fallbacks.
    """

    TIMEOUT_SECONDS = 4.0

    @classmethod
    def parse_platform_identifier(cls, platform: str, canonical_url: str, canonical_id: Optional[str] = None) -> str:
        """
        Extracts clean search identifier for the given platform:
        - Amazon: ASIN (10 alphanumeric chars)
        - Flipkart: PID (e.g. MOB...)
        - Myntra: Style ID (numeric)
        - AJIO: 9-digit style code
        - Nykaa: SKU ID
        """
        if canonical_id and str(canonical_id).strip():
            return str(canonical_id).strip()

        p = platform.lower()
        url = canonical_url.strip()

        if "amazon" in p:
            # Match /dp/B0...
            m = re.search(r'/(?:dp|gp/product)/([A-Z0-9]{10})', url, re.I)
            if m:
                return m.group(1).upper()

        elif "flipkart" in p:
            # Match pid=... or /p/itm...
            m = re.search(r'[?&]pid=([A-Za-z0-9_-]+)', url)
            if m:
                return m.group(1)
            m = re.search(r'/p/(itm[a-zA-Z0-9]+)', url)
            if m:
                return m.group(1)

        elif "myntra" in p:
            # Match numeric style ID
            m = re.search(r'/(\d{5,12})(?:/buy)?/?', url)
            if m:
                return m.group(1)

        elif "ajio" in p:
            # Match product style code e.g. /p/469034293_blue or 469034293
            m = re.search(r'/p/([a-zA-Z0-9_-]+)', url)
            if m:
                return m.group(1)

        elif "nykaa" in p:
            # Match skuId=...
            m = re.search(r'[?&]skuId=(\d+)', url)
            if m:
                return m.group(1)

        return canonical_id or url

    @classmethod
    def extract_time_series_from_text(cls, text: str) -> List[Tuple[int, float]]:
        """
        Locates and parses Highcharts/JSON [[timestamp_ms, price], ...] coordinates from HTML or scripts.
        """
        if not text:
            return []

        # 1. Check primary Highcharts regex pattern
        match = HIGHCHARTS_DATA_REGEX.search(text)
        if not match:
            match = SERIES_SERIES_REGEX.search(text)

        if match:
            try:
                raw_json = match.group(1)
                data = json.loads(raw_json)
                if isinstance(data, list):
                    points: List[Tuple[int, float]] = []
                    for item in data:
                        if isinstance(item, (list, tuple)) and len(item) >= 2:
                            ts, pr = item[0], item[1]
                            if isinstance(ts, (int, float)) and isinstance(pr, (int, float)):
                                points.append((int(ts), float(pr)))
                    return points
            except Exception as exc:
                logger.debug(f"Regex matched but JSON load failed: {exc}")

        # 2. Check direct JSON object payloads
        try:
            # Check if response is raw JSON containing a points list
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                candidates = parsed.get("data") or parsed.get("points") or parsed.get("history") or []
                if isinstance(candidates, list) and candidates and isinstance(candidates[0], (list, tuple)):
                    return [(int(x[0]), float(x[1])) for x in candidates if len(x) >= 2]
        except Exception:
            pass

        return []

    @classmethod
    def normalize_and_downsample(cls, raw_points: List[Tuple[int, float]]) -> List[Dict[str, Any]]:
        """
        Data Normalization Pipeline:
        1. Sort chronological ascending.
        2. Convert millisecond timestamps to UTC datetime.
        3. Filter invalid data (price <= 0).
        4. Filter unrealistic glitch spikes/drops (>90% in < 24h).
        5. Downsample records to 1 price point per day (recording the daily minimum price).
        """
        if not raw_points:
            return []

        # Sort chronologically
        sorted_points = sorted(raw_points, key=lambda x: x[0])

        valid_points: List[Tuple[datetime, float]] = []
        last_dt: Optional[datetime] = None
        last_price: Optional[float] = None

        for ts_ms, price in sorted_points:
            # Ignore invalid pricing
            if price <= 0:
                continue

            try:
                dt = datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc)
            except Exception:
                continue

            # Outlier filter: detect single-day artificial spikes/drops >90%
            if last_price is not None and last_dt is not None:
                delta_seconds = abs((dt - last_dt).total_seconds())
                if delta_seconds <= 86400:
                    percent_change = abs(price - last_price) / last_price
                    if percent_change > 0.90:
                        # Skip sudden erroneous spike/dump glitch
                        continue

            valid_points.append((dt, price))
            last_dt = dt
            last_price = price

        if not valid_points:
            return []

        # Group by UTC day and retain daily minimum price
        daily_mins: Dict[date, Tuple[datetime, float]] = {}
        for dt, price in valid_points:
            d = dt.date()
            if d not in daily_mins or price < daily_mins[d][1]:
                daily_mins[d] = (dt, price)

        # Build output list
        output: List[Dict[str, Any]] = [
            {"recorded_at": dt, "price": round(price, 2)}
            for d, (dt, price) in sorted(daily_mins.items(), key=lambda x: x[0])
        ]
        return output

    @classmethod
    async def fetch_history(
        cls,
        platform: str,
        canonical_url: str,
        canonical_id: str
    ) -> List[Dict[str, Any]]:
        """
        Attempts to query public price chart aggregators within a strict 4-second timeout.
        Returns a normalized list of {"recorded_at": datetime, "price": float}.
        Returns [] gracefully if unindexed or if any network error occurs.
        """
        identifier = cls.parse_platform_identifier(platform, canonical_url, canonical_id)
        if not identifier:
            return []

        # Prepare target search / aggregation queries across public endpoints
        search_urls = [
            f"https://pricebefore.com/search/?q={quote_plus(identifier)}",
            f"https://pricehistoryapp.com/api/search?q={quote_plus(identifier)}",
            f"https://pricehistory.in/search?q={quote_plus(identifier)}",
        ]

        # Also add direct canonical URL search if different
        if canonical_url and canonical_url != identifier:
            search_urls.append(f"https://pricebefore.com/search/?q={quote_plus(canonical_url)}")

        raw_points: List[Tuple[int, float]] = []

        try:
            async with httpx.AsyncClient(
                headers=DESKTOP_HEADERS,
                timeout=cls.TIMEOUT_SECONDS,
                follow_redirects=True
            ) as client:
                for target_url in search_urls:
                    try:
                        response = await client.get(target_url)
                        if response.status_code == 200:
                            extracted = cls.extract_time_series_from_text(response.text)
                            if extracted:
                                raw_points = extracted
                                logger.info(f"Retrieved {len(raw_points)} historical points from {target_url} for {identifier}")
                                break
                    except (httpx.TimeoutException, httpx.RequestError) as net_err:
                        logger.debug(f"Aggregator query timeout/error for {target_url}: {net_err}")
                        continue
        except Exception as exc:
            logger.warning(f"Unexpected error in HistoricalAggregatorService for {identifier}: {exc}")
            return []

        # Normalize and downsample points
        return cls.normalize_and_downsample(raw_points)
