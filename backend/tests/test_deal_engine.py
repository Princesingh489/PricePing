"""
Unit and Integration Tests for Live Deal Engine & Validator
===========================================================
Validates:
- Strict deal validation rules (URL, image, price, MRP, availability, store, freshness).
- Transparent deal score computation.
- Historical best / low badge detection (30-day low, 7-day low).
- 5-store balanced ranking (Amazon, Flipkart, Myntra, AJIO, Nykaa).
- Automatic replacement of expired / out-of-stock deals.
- API response contract for /api/trending-deals.
"""

import pytest
from datetime import datetime, timezone, timedelta

from services.deal_validator import DealValidator
from services.deal_engine import DealEngine
from services.trending_engine import TrendingEngine
from db.database import SessionLocal
from db import models


def test_validator_rejects_unsupported_store():
    is_valid, msg = DealValidator.validate_store("snapdeal")
    assert is_valid is False
    assert "not one of the 5 supported stores" in msg

    is_valid, msg = DealValidator.validate_store("myntra")
    assert is_valid is True


def test_validator_rejects_mismatched_and_invalid_urls():
    # Store mismatch: Amazon store with flipkart url
    is_valid, msg = DealValidator.validate_url("https://www.flipkart.com/item/p/123", "amazon")
    assert is_valid is False
    assert "does not match store 'amazon'" in msg

    # Invalid scheme
    is_valid, msg = DealValidator.validate_url("ftp://www.amazon.in/dp/B123", "amazon")
    assert is_valid is False

    # Valid Myntra URL
    is_valid, msg = DealValidator.validate_url("https://www.myntra.com/trousers/broadstar/36968033/buy", "myntra")
    assert is_valid is True


def test_validator_rejects_placeholder_and_broken_images():
    # Placeholder string rejection
    is_valid, msg = DealValidator.validate_image("https://assets.myntassets.com/placeholder-image.jpg")
    assert is_valid is False
    assert "generic placeholder" in msg

    # Unrecognized untrusted CDN without image extension
    is_valid, msg = DealValidator.validate_image("https://random-unknown-site.xyz/data")
    assert is_valid is False

    # Valid trusted CDN image
    is_valid, msg = DealValidator.validate_image("https://assets.myntassets.com/v1/assets/images/image.jpg")
    assert is_valid is True

    # Valid Unsplash image
    is_valid, msg = DealValidator.validate_image("https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=500")
    assert is_valid is True


def test_validator_price_and_mrp_checks():
    # Zero price rejection
    is_valid, msg = DealValidator.validate_price_and_mrp(0.0, 1000.0)
    assert is_valid is False

    # Negative price rejection
    is_valid, msg = DealValidator.validate_price_and_mrp(-500.0, 1000.0)
    assert is_valid is False

    # MRP < price rejection
    is_valid, msg = DealValidator.validate_price_and_mrp(1200.0, 999.0)
    assert is_valid is False
    assert "cannot be lower than current selling price" in msg

    # Valid price & MRP
    is_valid, msg = DealValidator.validate_price_and_mrp(899.0, 1999.0)
    assert is_valid is True


def test_validator_freshness_calculation():
    now = datetime.now(timezone.utc)

    # 2 minutes ago -> LIVE
    state, label, _ = DealValidator.calculate_freshness(now - timedelta(minutes=2))
    assert state == "LIVE"
    assert "Price verified" in label

    # 10 minutes ago -> RECENT
    state, label, _ = DealValidator.calculate_freshness(now - timedelta(minutes=10))
    assert state == "RECENT"

    # 25 minutes ago -> STALE
    state, label, _ = DealValidator.calculate_freshness(now - timedelta(minutes=25))
    assert state == "STALE"

    # 90 minutes ago -> EXPIRED
    state, label, _ = DealValidator.calculate_freshness(now - timedelta(minutes=90))
    assert state == "EXPIRED"


def test_deal_score_and_historical_low_detection():
    now = datetime.now(timezone.utc) - timedelta(minutes=1)

    # 30-day low detection
    score, badge = DealEngine.calculate_deal_score(
        price=799.0,
        mrp=1499.0,
        lowest_30d=799.0,
        average_30d=1199.0,
        rating=4.6,
        rating_count=5000,
        last_verified_at=now,
    )
    assert badge == "🔥 30-day low"
    assert score >= 75.0

    # 7-day low detection
    score_7d, badge_7d = DealEngine.calculate_deal_score(
        price=899.0,
        mrp=1499.0,
        lowest_30d=799.0,
        lowest_7d=899.0,
        average_30d=1199.0,
        rating=4.3,
        rating_count=2000,
        last_verified_at=now,
    )
    assert badge_7d == "⚡ 7-day low"
    assert score_7d > 60.0


def test_5_store_balanced_ranking():
    now = datetime.now(timezone.utc) - timedelta(minutes=1)

    # Create 30 mock candidates (6 from each of the 5 stores)
    mock_candidates = []
    for store in ["amazon", "flipkart", "myntra", "ajio", "nykaa"]:
        for i in range(6):
            mock_candidates.append({
                "deal_key": f"{store}_{i}",
                "store": store,
                "title": f"Sample {store.capitalize()} Product {i}",
                "product_url": f"https://www.{store}.com/item/{i}" if store != "amazon" else f"https://www.amazon.in/dp/{i}",
                "image_url": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=500",
                "price": 500.0 + (i * 50),
                "mrp": 1000.0 + (i * 100),
                "availability": "in_stock",
                "rating": 4.5,
                "rating_count": 3000,
                "last_verified_at": now,
            })

    ranked_deals = DealEngine.rank_and_balance_deals(mock_candidates, target_total=20, per_store_target=4)

    assert len(ranked_deals) == 20
    # Verify all 5 stores are present
    stores_present = {d["store"] for d in ranked_deals}
    assert stores_present == {"amazon", "flipkart", "myntra", "ajio", "nykaa"}

    # Verify each store has at least 4 deals
    for s in ["amazon", "flipkart", "myntra", "ajio", "nykaa"]:
        store_deals = [d for d in ranked_deals if d["store"] == s]
        assert len(store_deals) >= 4


def test_automatic_replacement_system():
    now = datetime.now(timezone.utc) - timedelta(minutes=1)
    active = [
        {"deal_key": "d1", "store": "myntra", "title": "Myntra Product 1", "deal_score": 90, "last_verified_at": now, "availability": "in_stock", "price": 500, "mrp": 1000, "product_url": "https://www.myntra.com/p1", "image_url": "https://images.unsplash.com/p1.jpg"},
        {"deal_key": "d2", "store": "amazon", "title": "Amazon Product 2", "deal_score": 85, "last_verified_at": now, "availability": "in_stock", "price": 800, "mrp": 1200, "product_url": "https://www.amazon.in/dp/p2", "image_url": "https://images.unsplash.com/p2.jpg"},
    ]
    reserve = [
        {"deal_key": "d3", "store": "myntra", "title": "Myntra Product 3", "deal_score": 88, "last_verified_at": now, "availability": "in_stock", "price": 600, "mrp": 1100, "product_url": "https://www.myntra.com/p3", "image_url": "https://images.unsplash.com/p3.jpg"},
    ]

    # Replace d1 (e.g. Price changed or Out of Stock)
    updated = DealEngine.replace_invalid_deal(active, "d1", reserve)
    assert len(updated) == 2
    keys = [d["deal_key"] for d in updated]
    assert "d1" not in keys
    assert "d3" in keys
    assert "d2" in keys


def test_trending_engine_cache_and_response():
    db = SessionLocal()
    try:
        res = TrendingEngine.get_trending_deals(db)
        assert "deals" in res
        assert "updated_at" in res
        assert "stores_represented" in res
        assert len(res["deals"]) > 0

        # Check all 5 stores are present in live feed
        stores = set(res["stores_represented"])
        for expected_store in ["amazon", "flipkart", "myntra", "ajio", "nykaa"]:
            assert expected_store in stores

        # Test store filter
        ajio_res = TrendingEngine.get_trending_deals(db, store_filter="ajio")
        for deal in ajio_res["deals"]:
            assert deal["store"] == "ajio"
    finally:
        db.close()
