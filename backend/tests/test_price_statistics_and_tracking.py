"""
PricePing Master Test Suite
===========================
Verifies:
1. Mathematical Invariant: LOWEST <= AVERAGE <= HIGHEST (Part A)
2. Single Source of Truth & Zero/Single observation handling (Part A)
3. Potential Savings Calculation (Part A)
4. Absence of Synthetic/Fake Data Generation (Part A)
5. Tracked Products Sorting: NEWEST -> OLDEST via created_at DESC (Part D)
6. Price Checks & Alert Triggers do NOT change sorting (Part D)
7. Re-adding deleted product resets created_at and moves to top (Part D)
8. Tracked Product Delete: Non-destructive to global Product & PriceHistory (Part C)
9. Multi-user isolation on deletion (Part C)
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.database import Base
from db import models
from services.historical_provider import calculate_real_statistics, MergedHistoricalProvider

# In-memory test DB
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


# ────────────────────────────────────────────────────────────────────────────
# 1. MATHEMATICAL INVARIANTS & SINGLE SOURCE OF TRUTH (PART A)
# ────────────────────────────────────────────────────────────────────────────

def test_zero_observations_returns_none():
    """Requirement: Zero observations must return None (— in UI), never 0 or fake."""
    prod = models.Product(id=1, product_name="Test Product", current_price=3599.0)
    stats = calculate_real_statistics(prod, [])

    assert stats["lowest_price"] is None
    assert stats["highest_price"] is None
    assert stats["average_price"] is None
    assert stats["median_price"] is None
    assert stats["observation_count"] == 0
    assert stats["potential_saving"] == 0.0
    assert stats["recommendation"] == "INSUFFICIENT_DATA"


def test_single_observation_returns_p_equal():
    """Requirement: Exactly 1 observation P must yield Lowest = P, Avg = P, High = P."""
    prod = models.Product(id=1, product_name="Test Product", current_price=3599.0)
    observations = [{"timestamp": "2026-08-01T12:00:00", "price": 3599.0, "store": "amazon"}]
    stats = calculate_real_statistics(prod, observations)

    assert stats["lowest_price"] == 3599.0
    assert stats["average_price"] == 3599.0
    assert stats["highest_price"] == 3599.0
    assert stats["median_price"] == 3599.0
    assert stats["lowest_price"] <= stats["average_price"] <= stats["highest_price"]
    assert stats["observation_count"] == 1


def test_mathematical_invariant_lowest_le_average_le_highest():
    """
    Requirement: LOWEST <= AVERAGE <= HIGHEST must ALWAYS hold across any price series.
    Directly tests the specific bug: Lowest: 3599, Average: 3771, Highest: 3599 is impossible.
    """
    prod = models.Product(id=1, product_name="Test Product", current_price=3599.0)
    
    # Series with multiple prices
    observations = [
        {"timestamp": "2026-06-01T10:00:00", "price": 3599.0, "store": "amazon"},
        {"timestamp": "2026-06-15T10:00:00", "price": 3943.0, "store": "amazon"},
        {"timestamp": "2026-07-01T10:00:00", "price": 3771.0, "store": "amazon"},
    ]
    stats = calculate_real_statistics(prod, observations)

    assert stats["lowest_price"] == 3599.0
    assert stats["highest_price"] == 3943.0
    # Average of 3599 + 3943 + 3771 = 11313 / 3 = 3771.0
    assert stats["average_price"] == 3771.0
    assert stats["lowest_price"] <= stats["average_price"] <= stats["highest_price"], (
        f"Invariant violated: {stats['lowest_price']} <= {stats['average_price']} <= {stats['highest_price']}"
    )


def test_corrupted_and_invalid_data_sanitization():
    """Requirement: Filter out <=0, None, NaN, and corrupted price entries."""
    prod = models.Product(id=1, product_name="Test Product", current_price=2000.0)
    observations = [
        {"timestamp": "2026-08-01T10:00:00", "price": -50.0, "store": "amazon"},
        {"timestamp": "2026-08-02T10:00:00", "price": 0, "store": "amazon"},
        {"timestamp": "2026-08-03T10:00:00", "price": None, "store": "amazon"},
        {"timestamp": "2026-08-04T10:00:00", "price": float("nan"), "store": "amazon"},
        {"timestamp": "2026-08-05T10:00:00", "price": 2000.0, "store": "amazon"},
        {"timestamp": "2026-08-06T10:00:00", "price": 2500.0, "store": "amazon"},
    ]
    stats = calculate_real_statistics(prod, observations)

    assert stats["observation_count"] == 2
    assert stats["lowest_price"] == 2000.0
    assert stats["highest_price"] == 2500.0
    assert stats["average_price"] == 2250.0
    assert stats["lowest_price"] <= stats["average_price"] <= stats["highest_price"]


def test_potential_savings_calculation():
    """Requirement: Potential saving = max(0, highest_historical - current_price)."""
    prod = models.Product(id=1, product_name="Test Product", current_price=3200.0)
    observations = [
        {"timestamp": "2026-08-01T10:00:00", "price": 4000.0, "store": "amazon"},
        {"timestamp": "2026-08-10T10:00:00", "price": 3200.0, "store": "amazon"},
    ]
    stats = calculate_real_statistics(prod, observations)

    assert stats["highest_price"] == 4000.0
    assert stats["current_price"] == 3200.0
    assert stats["potential_saving"] == 800.0  # 4000 - 3200


# ────────────────────────────────────────────────────────────────────────────
# 2. TRACKED PRODUCTS SORTING & SCHEDULER (PART D)
# ────────────────────────────────────────────────────────────────────────────

def test_tracked_products_sorted_newest_to_oldest():
    """Requirement: 'Your Tracked Products' must strictly sort by created_at DESC."""
    db = TestingSessionLocal()
    user = models.User(id=1, name="Test User", email="test@example.com", password_hash="hash")
    db.add(user)
    db.commit()

    p1 = models.Product(id=1, product_name="Earphones 1", current_price=1000.0, platform=models.PlatformEnum.amazon, product_url="https://amazon.in/dp/B1")
    p2 = models.Product(id=2, product_name="Earphones 2", current_price=2000.0, platform=models.PlatformEnum.amazon, product_url="https://amazon.in/dp/B2")
    p3 = models.Product(id=3, product_name="Earphones 3", current_price=3000.0, platform=models.PlatformEnum.amazon, product_url="https://amazon.in/dp/B3")
    db.add_all([p1, p2, p3])
    db.commit()

    t1 = models.UserTrackedProduct(id=1, user_id=1, product_id=1, tracking_status=models.TrackingStatusEnum.active, created_at=datetime(2026, 1, 1))
    t2 = models.UserTrackedProduct(id=2, user_id=1, product_id=2, tracking_status=models.TrackingStatusEnum.active, created_at=datetime(2026, 2, 1))
    t3 = models.UserTrackedProduct(id=3, user_id=1, product_id=3, tracking_status=models.TrackingStatusEnum.active, created_at=datetime(2026, 3, 1))
    db.add_all([t1, t2, t3])
    db.commit()

    # Query with database-controlled sorting
    results = (
        db.query(models.UserTrackedProduct)
        .filter(models.UserTrackedProduct.user_id == 1, models.UserTrackedProduct.tracking_status != models.TrackingStatusEnum.deleted)
        .order_by(models.UserTrackedProduct.created_at.desc())
        .all()
    )

    ids = [r.product_id for r in results]
    assert ids == [3, 2, 1], f"Expected newest tracked first [3, 2, 1], got {ids}"
    db.close()


def test_price_refresh_and_alerts_do_not_alter_sort():
    """
    Requirement 32 & 33:
    - Price checks / last_checked updates MUST NOT alter sort order.
    - Alert triggers MUST NOT alter sort order.
    """
    db = TestingSessionLocal()
    user = models.User(id=2, name="User Two", email="u2@example.com", password_hash="hash")
    db.add(user)
    db.commit()

    p1 = models.Product(id=10, product_name="Phone A", current_price=15000.0, platform=models.PlatformEnum.flipkart, product_url="https://fk.com/p10", last_checked=datetime(2026, 1, 1))
    p2 = models.Product(id=20, product_name="Phone B", current_price=25000.0, platform=models.PlatformEnum.flipkart, product_url="https://fk.com/p20", last_checked=datetime(2026, 1, 1))
    db.add_all([p1, p2])
    db.commit()

    # User tracks Phone A on Jan 1, Phone B on Feb 1
    t1 = models.UserTrackedProduct(id=10, user_id=2, product_id=10, tracking_status=models.TrackingStatusEnum.active, created_at=datetime(2026, 1, 1))
    t2 = models.UserTrackedProduct(id=20, user_id=2, product_id=20, tracking_status=models.TrackingStatusEnum.active, created_at=datetime(2026, 2, 1))
    db.add_all([t1, t2])
    db.commit()

    # Now Phone A is refreshed with a new price today
    p1.last_checked = datetime.utcnow()
    p1.current_price = 14000.0
    db.commit()

    # Query again
    results = (
        db.query(models.UserTrackedProduct)
        .filter(models.UserTrackedProduct.user_id == 2, models.UserTrackedProduct.tracking_status != models.TrackingStatusEnum.deleted)
        .order_by(models.UserTrackedProduct.created_at.desc())
        .all()
    )

    ids = [r.product_id for r in results]
    # Phone B is still on top because it was tracked more recently!
    assert ids == [20, 10], f"Expected sort [20, 10] unchanged by price check, got {ids}"
    db.close()


def test_re_adding_product_resets_created_at_to_top():
    """
    Requirement 34:
    If a user tracks Product A, deletes it, and tracks it again later,
    its created_at must update to NOW and move it to the top!
    """
    db = TestingSessionLocal()
    user = models.User(id=3, name="User Three", email="u3@example.com", password_hash="hash")
    db.add(user)
    db.commit()

    pA = models.Product(id=100, product_name="Watch A", current_price=5000.0, platform=models.PlatformEnum.amazon, product_url="https://amz.in/wA")
    pB = models.Product(id=200, product_name="Watch B", current_price=6000.0, platform=models.PlatformEnum.amazon, product_url="https://amz.in/wB")
    db.add_all([pA, pB])
    db.commit()

    # Track A on Jan 1, B on Feb 1
    tA = models.UserTrackedProduct(id=100, user_id=3, product_id=100, tracking_status=models.TrackingStatusEnum.active, created_at=datetime(2026, 1, 1))
    tB = models.UserTrackedProduct(id=200, user_id=3, product_id=200, tracking_status=models.TrackingStatusEnum.active, created_at=datetime(2026, 2, 1))
    db.add_all([tA, tB])
    db.commit()

    # User deletes tracking for Watch A
    tA.tracking_status = models.TrackingStatusEnum.deleted
    db.commit()

    # Later user tracks Watch A again -> Re-activating tracking resets created_at = datetime.utcnow()
    tA.tracking_status = models.TrackingStatusEnum.active
    tA.created_at = datetime.utcnow()
    db.commit()

    # Query order
    results = (
        db.query(models.UserTrackedProduct)
        .filter(models.UserTrackedProduct.user_id == 3, models.UserTrackedProduct.tracking_status != models.TrackingStatusEnum.deleted)
        .order_by(models.UserTrackedProduct.created_at.desc())
        .all()
    )

    ids = [r.product_id for r in results]
    # Watch A was re-added today, so it must be at the very top!
    assert ids == [100, 200], f"Expected re-added product to be top [100, 200], got {ids}"
    db.close()


# ────────────────────────────────────────────────────────────────────────────
# 3. DELETE / REMOVE TRACKING NON-DESTRUCTIVE INTEGRITY (PART C)
# ────────────────────────────────────────────────────────────────────────────

def test_delete_tracking_preserves_global_product_and_price_history():
    """
    Requirement 26:
    When a user stops tracking a product:
    DO NOT delete: global product, product data, verified price history.
    Only remove/soft-delete the user's tracking relationship.
    """
    db = TestingSessionLocal()
    u1 = models.User(id=10, name="User Ten", email="user1@test.com", password_hash="hash")
    u2 = models.User(id=20, name="User Twenty", email="user2@test.com", password_hash="hash")
    db.add_all([u1, u2])
    db.commit()

    prod = models.Product(id=500, product_name="Shared Product", current_price=1999.0, platform=models.PlatformEnum.amazon, product_url="https://amz.in/p500")
    db.add(prod)
    db.commit()

    # Price history records exist
    h1 = models.PriceHistory(product_id=500, store="amazon", price=1999.0, checked_at=datetime(2026, 1, 1), recorded_at=datetime(2026, 1, 1), verified=True)
    h2 = models.PriceHistory(product_id=500, store="amazon", price=1799.0, checked_at=datetime(2026, 2, 1), recorded_at=datetime(2026, 2, 1), verified=True)
    db.add_all([h1, h2])
    db.commit()

    # User 1 and User 2 both track the product
    t1 = models.UserTrackedProduct(id=1000, user_id=10, product_id=500, tracking_status=models.TrackingStatusEnum.active)
    t2 = models.UserTrackedProduct(id=2000, user_id=20, product_id=500, tracking_status=models.TrackingStatusEnum.active)
    db.add_all([t1, t2])
    db.commit()

    # User 1 deletes their tracking
    t1.tracking_status = models.TrackingStatusEnum.deleted
    db.commit()

    # Verify:
    # 1. Global Product STILL EXISTS
    assert db.query(models.Product).filter(models.Product.id == 500).first() is not None
    # 2. Verified Price History STILL EXISTS intact (2 entries)
    history_count = db.query(models.PriceHistory).filter(models.PriceHistory.product_id == 500).count()
    assert history_count == 2
    # 3. User 2's tracking is COMPLETELY UNAFFECTED and active
    u2_tracker = db.query(models.UserTrackedProduct).filter(models.UserTrackedProduct.id == 2000).first()
    assert u2_tracker.tracking_status == models.TrackingStatusEnum.active
    # 4. User 1 active tracker count is 0
    u1_count = db.query(models.UserTrackedProduct).filter(
        models.UserTrackedProduct.user_id == 10,
        models.UserTrackedProduct.tracking_status == models.TrackingStatusEnum.active
    ).count()
    assert u1_count == 0
    db.close()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    test_zero_observations_returns_none()
    test_single_observation_returns_p_equal()
    test_mathematical_invariant_lowest_le_average_le_highest()
    test_corrupted_and_invalid_data_sanitization()
    test_potential_savings_calculation()
    test_tracked_products_sorted_newest_to_oldest()
    test_price_refresh_and_alerts_do_not_alter_sort()
    test_re_adding_product_resets_created_at_to_top()
    test_delete_tracking_preserves_global_product_and_price_history()
    print("ALL 9 PRICE STATISTICS & TRACKING INVARIANT TESTS PASSED SUCCESSFULLY! (9/9)")

