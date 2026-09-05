"""
DealScoreService
================
Computes a deal recommendation (BUY_NOW / WAIT / WATCH / INSUFFICIENT_DATA)
based exclusively on verified, real price history observations stored in the DB.

STRICT DATA INTEGRITY RULE:
- NEVER use synthetic or interpolated price data.
- If fewer than 5 real history points exist → return INSUFFICIENT_DATA.
- Lowest/Highest values come only from real observations, never from estimates.
"""
from __future__ import annotations

import logging
import statistics
from typing import List, Literal, Optional, NamedTuple

from db import models

logger = logging.getLogger(__name__)

# Minimum real data points required before issuing a recommendation
MIN_HISTORY_POINTS = 5

# Thresholds (percentile of current price within the historical range)
EXCELLENT_DEAL_PERCENTILE = 15.0   # Current price is in bottom 15% → BUY_NOW
GOOD_DEAL_PERCENTILE = 35.0        # Current price in bottom 35% → WATCH
# Above 35% → WAIT


class DealScore(NamedTuple):
    recommendation: Literal["BUY_NOW", "WAIT", "WATCH", "INSUFFICIENT_DATA"]
    confidence: int           # 0–100 integer confidence
    percentile: Optional[float]  # 0 = lowest, 100 = highest, None if insufficient data
    avg_price: Optional[float]
    lowest_price: Optional[float]
    highest_price: Optional[float]
    data_points: int
    tracking_days: int
    message: str


def compute_deal_score(
    product: models.Product,
    history: List[models.PriceHistory],
) -> DealScore:
    """
    Analyse real price history and return a deal recommendation.

    Args:
        product: The Product ORM object.
        history: All real PriceHistory records for this product (ordered by date asc).

    Returns:
        DealScore with recommendation and supporting statistics.
    """
    data_points = len(history)

    # Compute tracking duration in days from earliest to latest record
    if data_points >= 2:
        earliest = history[0].checked_at
        latest = history[-1].checked_at
        delta = latest - earliest
        tracking_days = max(delta.days, 1)
    elif data_points == 1:
        tracking_days = 1
    else:
        tracking_days = 0

    # ----------------------------------------------------------------
    # Guard: INSUFFICIENT DATA
    # ----------------------------------------------------------------
    if data_points < MIN_HISTORY_POINTS or product.current_price is None:
        return DealScore(
            recommendation="INSUFFICIENT_DATA",
            confidence=0,
            percentile=None,
            avg_price=None,
            lowest_price=product.lowest_price,
            highest_price=product.highest_price,
            data_points=data_points,
            tracking_days=tracking_days,
            message=(
                "We're still building the price history for this product. "
                "Check back after a few more price checks to see buying recommendations."
            ),
        )

    # ----------------------------------------------------------------
    # Core statistics from real observations only
    # ----------------------------------------------------------------
    prices = [h.price for h in history if h.price is not None]
    if not prices:
        return DealScore(
            recommendation="INSUFFICIENT_DATA",
            confidence=0,
            percentile=None,
            avg_price=None,
            lowest_price=None,
            highest_price=None,
            data_points=0,
            tracking_days=tracking_days,
            message="No valid price records found.",
        )

    lowest = min(prices)
    highest = max(prices)
    avg = statistics.mean(prices)
    current = product.current_price

    price_range = highest - lowest

    # Compute percentile: where does the current price sit in the history?
    # 0 = at the lowest ever, 100 = at the highest ever
    if price_range > 0:
        raw_percentile = ((current - lowest) / price_range) * 100.0
        percentile = max(0.0, min(100.0, raw_percentile))
    else:
        # All recorded prices are the same
        percentile = 50.0

    # ----------------------------------------------------------------
    # Recommendation logic
    # ----------------------------------------------------------------
    if percentile <= EXCELLENT_DEAL_PERCENTILE:
        recommendation: Literal["BUY_NOW", "WAIT", "WATCH", "INSUFFICIENT_DATA"] = "BUY_NOW"
        # Confidence is higher when more data points exist and current price is closer to all-time low
        base_confidence = 90 - int(percentile * 2)  # 90 at percentile=0, 60 at percentile=15
        data_bonus = min(data_points, 50)  # Up to +50 bonus for data richness, capped at 10
        data_bonus = min(data_bonus // 10, 10)
        confidence = min(base_confidence + data_bonus, 99)
        message = (
            f"🔥 Excellent deal! Current price (₹{current:,.0f}) is near its all-time low "
            f"of ₹{lowest:,.0f}. Historically, it's been higher {100 - percentile:.0f}% of the time."
        )

    elif percentile <= GOOD_DEAL_PERCENTILE:
        recommendation = "WATCH"
        confidence = max(40, 75 - int(percentile))
        message = (
            f"👀 Decent price. Current price (₹{current:,.0f}) is below average "
            f"(avg ₹{avg:,.0f}), but may still dip lower. Consider setting an alert."
        )

    else:
        recommendation = "WAIT"
        confidence = max(30, 60 - int(percentile // 2))
        savings_potential = current - lowest
        message = (
            f"⏳ Hold on. Current price (₹{current:,.0f}) is above average (avg ₹{avg:,.0f}). "
            f"This product has dropped to ₹{lowest:,.0f} before — potential saving of ₹{savings_potential:,.0f}."
        )

    logger.info(
        f"[DealScore] Product {product.id}: {recommendation} "
        f"(percentile={percentile:.1f}, points={data_points}, "
        f"current={current}, avg={avg:.0f}, low={lowest}, high={highest})"
    )

    return DealScore(
        recommendation=recommendation,
        confidence=confidence,
        percentile=round(percentile, 2),
        avg_price=round(avg, 2),
        lowest_price=round(lowest, 2),
        highest_price=round(highest, 2),
        data_points=data_points,
        tracking_days=tracking_days,
        message=message,
    )
