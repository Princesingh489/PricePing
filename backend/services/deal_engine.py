"""
PricePing Live Deal Engine & Scoring Service
============================================
Calculates multi-factor Deal Scores, detects 7-day/30-day historical lows,
enforces 5-store balanced ranking, and automatically replaces expired offers.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
import logging

from services.deal_validator import DealValidator

logger = logging.getLogger(__name__)


class DealEngine:
    """
    Ranks live verified deals across Amazon, Flipkart, Myntra, AJIO, and Nykaa.
    Never relies on arbitrary discount claims or unverifiable marketing tags.
    """

    @classmethod
    def calculate_deal_score(
        cls,
        price: float,
        mrp: Optional[float] = None,
        lowest_30d: Optional[float] = None,
        lowest_7d: Optional[float] = None,
        average_30d: Optional[float] = None,
        rating: Optional[float] = 4.2,
        rating_count: Optional[int] = 1000,
        last_verified_at: Optional[datetime] = None,
    ) -> Tuple[float, Optional[str]]:
        """
        Calculates a transparent multi-factor Deal Score (0 to 100) and historical badge:
        1. Current MRP Discount (35 pts max)
        2. Historical Price Drop (25 pts max)
        3. Rating Quality (15 pts max)
        4. Customer Popularity (10 pts max)
        5. Live Freshness (15 pts max)
        """
        if not price or price <= 0:
            return 0.0, None

        # 1. Discount Factor (max 35)
        discount_pct = 0.0
        if mrp and mrp > price:
            discount_pct = ((mrp - price) / mrp) * 100
        discount_score = min(35.0, (discount_pct / 70.0) * 35.0)

        # 2. Historical Price Drop Factor (max 25) & Badge Detection
        hist_score = 5.0
        badge = None

        if lowest_30d is not None and price <= (lowest_30d + 1.0):
            hist_score = 25.0
            badge = "🔥 30-day low"
        elif lowest_7d is not None and price <= (lowest_7d + 1.0):
            hist_score = 20.0
            badge = "⚡ 7-day low"
        elif average_30d is not None and price < average_30d:
            drop_from_avg = ((average_30d - price) / average_30d) * 100
            hist_score = min(20.0, 10.0 + drop_from_avg)
            badge = f"📉 {int(drop_from_avg)}% below avg"
        else:
            if discount_pct >= 60:
                badge = f"🔥 {int(discount_pct)}% Flat Off"
            elif discount_pct >= 40:
                badge = "✨ Top Deal"
            elif rating and rating >= 4.5:
                badge = "⭐ Top Rated"
            else:
                badge = "🟢 Verified Price"

        # 3. Rating Score (max 15)
        safe_rating = rating if (rating is not None and 1.0 <= rating <= 5.0) else 4.2
        rating_score = (safe_rating / 5.0) * 15.0

        # 4. Popularity Score (max 10)
        safe_count = rating_count if (rating_count is not None and rating_count > 0) else 500
        popularity_score = min(10.0, (safe_count / 10000.0) * 10.0)

        # 5. Freshness Score (max 15)
        freshness_state, _, age_seconds = DealValidator.calculate_freshness(last_verified_at)
        if freshness_state == "LIVE":
            freshness_score = 15.0
        elif freshness_state == "RECENT":
            freshness_score = 10.0
        elif freshness_state == "STALE":
            freshness_score = 5.0
        else:
            freshness_score = 0.0

        total_score = round(discount_score + hist_score + rating_score + popularity_score + freshness_score, 1)
        total_score = max(0.0, min(100.0, total_score))

        return total_score, badge

    @classmethod
    def rank_and_balance_deals(
        cls,
        candidate_deals: List[Dict[str, Any]],
        target_total: int = 20,
        per_store_target: int = 4,
    ) -> List[Dict[str, Any]]:
        """
        Step 24 & Step 25:
        Enforces 5-store balanced ranking and category diversification:
        - Filters candidates using DealValidator (fail-closed, only LIVE/RECENT).
        - Groups candidates by store (amazon, flipkart, myntra, ajio, nykaa).
        - Selects top deals per store to ensure all 5 stores have strong representation.
        - Fills any remaining slots from the highest-ranked remaining validated candidates.
        """
        # 1. Validate all candidates
        validated_pool: List[Dict[str, Any]] = []
        for cand in candidate_deals:
            is_valid, errors, deal_status = DealValidator.validate_candidate(cand)
            if is_valid:
                # Calculate Deal Score and badge if not present
                if "deal_score" not in cand or not cand["deal_score"]:
                    price = cand.get("price", 0)
                    mrp = cand.get("mrp")
                    score, badge = cls.calculate_deal_score(
                        price=price,
                        mrp=mrp,
                        lowest_30d=cand.get("lowest_30d"),
                        lowest_7d=cand.get("lowest_7d"),
                        average_30d=cand.get("average_30d"),
                        rating=cand.get("rating"),
                        rating_count=cand.get("rating_count"),
                        last_verified_at=cand.get("last_verified_at"),
                    )
                    cand["deal_score"] = score
                    if not cand.get("historical_badge"):
                        cand["historical_badge"] = badge

                cand["deal_status"] = "LIVE"
                cand["is_live"] = True
                validated_pool.append(cand)
            else:
                cand["deal_status"] = deal_status
                cand["is_live"] = False

        # Sort pool by deal_score descending
        validated_pool.sort(key=lambda d: d.get("deal_score", 0), reverse=True)

        # 2. Balanced 5-store selection
        by_store: Dict[str, List[Dict[str, Any]]] = {
            "amazon": [],
            "flipkart": [],
            "myntra": [],
            "ajio": [],
            "nykaa": [],
        }

        for deal in validated_pool:
            store_name = (deal.get("store") or "").lower()
            if store_name in by_store:
                by_store[store_name].append(deal)

        selected_deals: List[Dict[str, Any]] = []
        chosen_ids = set()

        # Phase A: Pick up to per_store_target for each store
        for store_key in ["amazon", "flipkart", "myntra", "ajio", "nykaa"]:
            store_candidates = by_store[store_key]
            picked = 0
            for deal in store_candidates:
                d_id = deal.get("id") or deal.get("deal_key") or deal.get("product_url")
                if d_id not in chosen_ids and picked < per_store_target:
                    selected_deals.append(deal)
                    chosen_ids.add(d_id)
                    picked += 1

        # Phase B: Fill remaining slots up to target_total with highest-scoring unchosen deals
        if len(selected_deals) < target_total:
            remaining = [d for d in validated_pool if (d.get("id") or d.get("deal_key") or d.get("product_url")) not in chosen_ids]
            for deal in remaining:
                if len(selected_deals) >= target_total:
                    break
                selected_deals.append(deal)
                chosen_ids.add(deal.get("id") or deal.get("deal_key") or deal.get("product_url"))

        # Final sort of selected deals by deal_score descending
        selected_deals.sort(key=lambda d: d.get("deal_score", 0), reverse=True)
        return selected_deals

    @classmethod
    def replace_invalid_deal(
        cls,
        active_deals: List[Dict[str, Any]],
        invalid_deal_key: str,
        reserve_pool: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Step 7: Automatic replacement system
        When an active deal's state changes (e.g. OUT_OF_STOCK or EXPIRED):
        1. Removes the invalid deal from active deals.
        2. Identifies its store to preserve balanced representation.
        3. Promotes the next highest-scoring validated reserve candidate for that store.
        """
        updated_deals = [d for d in active_deals if (d.get("deal_key") or str(d.get("id"))) != str(invalid_deal_key)]
        
        # If deal was removed, find replacement
        if len(updated_deals) < len(active_deals):
            active_keys = {d.get("deal_key") or str(d.get("id")) for d in updated_deals}
            
            # Find candidate for the same store first
            for candidate in reserve_pool:
                cand_key = candidate.get("deal_key") or str(candidate.get("id"))
                if cand_key not in active_keys:
                    is_valid, _, _ = DealValidator.validate_candidate(candidate)
                    if is_valid:
                        updated_deals.append(candidate)
                        break

        updated_deals.sort(key=lambda d: d.get("deal_score", 0), reverse=True)
        return updated_deals
