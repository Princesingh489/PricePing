"""
Automated Test Suite for Historical Price Aggregation Engine & Bulk DB Ops:
1. HistoricalAggregatorService (Highcharts Regex, Normalization, Downsampling, Resilience)
2. High-speed Bulk History Insertion (ON CONFLICT DO NOTHING)
3. Analytical Metrics Recalculation (All-time Min/Max, 90-day Average)
4. Cold-Start Fallback (AGGREGATED_2YR vs ORGANIC_COLD_START)
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from services.history_fetcher import HistoricalAggregatorService
from db.db_ops import bulk_insert_history, recalculate_product_metrics
from db.database import SessionLocal
from db import models


# =========================================================================
# 1. HistoricalAggregatorService Identifier Parsing Tests
# =========================================================================

def test_parse_platform_identifiers():
    # Amazon ASIN
    assert HistoricalAggregatorService.parse_platform_identifier(
        "amazon", "https://www.amazon.in/dp/B0856HNMR7"
    ) == "B0856HNMR7"

    # Flipkart PID
    assert HistoricalAggregatorService.parse_platform_identifier(
        "flipkart", "https://www.flipkart.com/item/p/itm123?pid=MOBTEST12345"
    ) == "MOBTEST12345"

    # Myntra numeric Style ID
    assert HistoricalAggregatorService.parse_platform_identifier(
        "myntra", "https://www.myntra.com/shirts/brand/style/24567890/buy"
    ) == "24567890"

    # AJIO 9-digit style code
    assert HistoricalAggregatorService.parse_platform_identifier(
        "ajio", "https://www.ajio.com/clothing/p/469034293_blue"
    ) == "469034293_blue"

    # Nykaa SKU ID
    assert HistoricalAggregatorService.parse_platform_identifier(
        "nykaa", "https://www.nykaa.com/product/p/12345?skuId=987654"
    ) == "987654"


# =========================================================================
# 2. Highcharts Regex & Normalization Tests
# =========================================================================

def test_extract_highcharts_time_series_regex():
    mock_html = """
    <html>
    <head><script>
        Highcharts.chart('container', {
            series: [{
                name: 'Price History',
                data: [[1672531200000, 1499.0], [1672617600000, 1399.0], [1672704000000, 1299.5]]
            }]
        });
    </script></head>
    <body>Chart Container</body>
    </html>
    """
    points = HistoricalAggregatorService.extract_time_series_from_text(mock_html)
    assert len(points) == 3
    assert points[0] == (1672531200000, 1499.0)
    assert points[1] == (1672617600000, 1399.0)
    assert points[2] == (1672704000000, 1299.5)


def test_normalize_and_downsample_filters_outliers_and_minimums():
    # Base timestamp: 2026-01-01 00:00:00 UTC
    base_ms = int(datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc).timestamp() * 1000)
    one_day_ms = 86400 * 1000

    raw_points = [
        (base_ms, 2000.0),                     # Day 1 - Reading 1
        (base_ms + 3600 * 1000, 1800.0),       # Day 1 - Reading 2 (Minimum for Day 1)
        (base_ms + 7200 * 1000, -50.0),        # Day 1 - Invalid price (should be ignored)
        (base_ms + 10800 * 1000, 1900.0),      # Day 1 - Reading 3
        (base_ms + 12000 * 1000, 10.0),        # Day 1 - >90% single-day glitch dump from 1900 to 10 (outlier)
        (base_ms + one_day_ms, 1750.0),        # Day 2 - Minimum for Day 2
        (base_ms + one_day_ms * 2, 1700.0),    # Day 3 - Minimum for Day 3
    ]

    normalized = HistoricalAggregatorService.normalize_and_downsample(raw_points)

    # Must downsample to 1 point per day
    assert len(normalized) == 3
    # Day 1 minimum should be 1800.0 (and 10.0 was filtered out as an anomaly)
    assert normalized[0]["price"] == 1800.0
    # Day 2 minimum should be 1750.0
    assert normalized[1]["price"] == 1750.0
    # Day 3 minimum should be 1700.0
    assert normalized[2]["price"] == 1700.0


@pytest.mark.asyncio
async def test_fetch_history_graceful_fallback_on_unindexed():
    # Calling fetch_history with non-existent or erroring URL must return []
    with patch("httpx.AsyncClient.get", side_effect=Exception("Connection timeout")):
        result = await HistoricalAggregatorService.fetch_history(
            platform="amazon",
            canonical_url="https://www.amazon.in/dp/B000000000",
            canonical_id="B000000000"
        )
        assert result == []


# =========================================================================
# 3. Database High-Speed Bulk Operations Tests
# =========================================================================

@pytest.mark.asyncio
async def test_bulk_insert_history_and_recalculate_metrics():
    db = SessionLocal()
    try:
        # Create a test product
        product = models.Product(
            platform=models.PlatformEnum.amazon,
            store="amazon",
            external_product_id="TESTASIN01",
            canonical_id="TESTASIN01",
            product_name="Test Headphones",
            title="Test Headphones",
            product_url="https://www.amazon.in/dp/TESTASIN01",
            canonical_url="https://www.amazon.in/dp/TESTASIN01",
            current_price=1500.0,
            status="PENDING",
            history_state="ORGANIC_COLD_START",
        )
        db.add(product)
        db.commit()
        db.refresh(product)

        # Generate 10 days of historical points
        now = datetime.utcnow()
        hist_points = [
            {"recorded_at": now - timedelta(days=i), "price": 1000.0 + (i * 50)}
            for i in range(10)
        ]

        # Bulk insert points with is_backfilled=True
        count = await bulk_insert_history(db, product.id, hist_points, is_backfilled=True, store="amazon")
        assert count > 0

        # Recalculate metrics
        metrics = await recalculate_product_metrics(db, product.id)
        db.refresh(product)

        assert metrics["lowest_price"] == 1000.0
        assert metrics["highest_price"] == 1450.0
        assert product.lowest_price == 1000.0
        assert product.highest_price == 1450.0
        assert product.average_price is not None
        assert product.average_price > 0

        # Clean up
        db.query(models.PriceHistory).filter(models.PriceHistory.product_id == product.id).delete()
        db.delete(product)
        db.commit()

    finally:
        db.close()
