"""
Flipkart Validators
"""
from typing import Optional, List, Tuple
from scrapers.shared.models import PriceCandidate


class FlipkartValidator:
    @classmethod
    def filter_and_rank_prices(
        cls,
        candidates: List[PriceCandidate],
        extracted_discount: Optional[float] = None,
    ) -> Tuple[Optional[float], Optional[float]]:
        selling_candidates = [c for c in candidates if c.category == "selling_price" and c.value and c.value > 0]
        mrp_candidates = [c for c in candidates if c.category == "mrp" and c.value and c.value > 0]

        # Prioritize MRP: highest confident MRP
        mrp_candidates.sort(key=lambda c: (c.confidence, c.value), reverse=True)
        mrp = mrp_candidates[0].value if mrp_candidates else None

        # Prioritize Selling Price:
        # 1. Look for explicit hero price selector (div.Nx9bqj.CxhGGd)
        hero_candidates = [c for c in selling_candidates if "CxhGGd" in getattr(c, "source", "")]
        if hero_candidates:
            selling_price = hero_candidates[0].value
        elif extracted_discount and mrp:
            # If discount badge is verified (e.g. 85%), find candidate closest to expected discounted price
            expected_price = mrp * (1.0 - (extracted_discount / 100.0))
            closest = min(selling_candidates, key=lambda c: abs(c.value - expected_price), default=None)
            if closest and abs(closest.value - expected_price) <= max(30.0, expected_price * 0.10):
                selling_price = closest.value
            else:
                selling_candidates.sort(key=lambda c: c.confidence, reverse=True)
                selling_price = selling_candidates[0].value if selling_candidates else None
        else:
            selling_candidates.sort(key=lambda c: c.confidence, reverse=True)
            selling_price = selling_candidates[0].value if selling_candidates else None

        if selling_price and mrp and selling_price > mrp:
            selling_price, mrp = mrp, selling_price

        return selling_price, mrp
