"""
Myntra Validators
"""
from typing import Optional, List, Tuple
from scrapers.shared.models import PriceCandidate


class MyntraValidator:
    @classmethod
    def filter_and_rank_prices(cls, candidates: List[PriceCandidate]) -> Tuple[Optional[float], Optional[float]]:
        selling_candidates = [c for c in candidates if c.category == "selling_price"]
        mrp_candidates = [c for c in candidates if c.category == "mrp"]

        selling_price = selling_candidates[0].value if selling_candidates else None
        mrp = mrp_candidates[0].value if mrp_candidates else None

        if selling_price and mrp and selling_price > mrp:
            selling_price, mrp = mrp, selling_price

        return selling_price, mrp
