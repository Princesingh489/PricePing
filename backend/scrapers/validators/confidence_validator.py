"""
Confidence Validator & Decision Engine
======================================
Evaluates evidence across DOM, JSON-LD, Metadata, and candidate classifications to assign a 0-100 confidence score and enforce fail-closed decision rules.
"""
from typing import Dict, Any, List, Optional
from scrapers.extractors.price_extractor import PriceCandidate


class ConfidenceValidator:
    ACCEPT_THRESHOLD = 85
    UNCERTAIN_THRESHOLD = 70

    @classmethod
    def calculate_confidence(
        cls,
        selected_price: Optional[float],
        candidates: List[PriceCandidate],
        has_main_container: bool,
        has_title: bool,
        has_image: bool,
        json_ld_price: Optional[float] = None,
    ) -> int:
        """
        Calculate 0-100 confidence score based on multi-source agreement and verification heuristics.
        """
        if selected_price is None or selected_price <= 0:
            return 0

        score = 0

        # Base candidate weight
        matching_candidates = [c for c in candidates if c.value == selected_price and c.label == "current_price"]
        if matching_candidates:
            best_cand = max(matching_candidates, key=lambda c: c.confidence_weight)
            score += best_cand.confidence_weight
        else:
            score += 20

        # Verified main container presence
        if has_main_container:
            score += 20

        # Title & Image sanity
        if has_title:
            score += 15
        if has_image:
            score += 10

        # JSON-LD cross-source agreement (+25)
        if json_ld_price is not None:
            if abs(json_ld_price - selected_price) <= 1.0:
                score += 25
            else:
                # Disagreement penalty
                score -= 20

        # Check if selected price collides with a known rejected coupon/offer candidate
        rejected_matches = [c for c in candidates if c.value == selected_price and c.confidence_weight < 0]
        if rejected_matches:
            score -= 80

        # Bound score between 0 and 100
        return max(0, min(100, score))

    @classmethod
    def is_acceptable(cls, confidence_score: int) -> bool:
        """Returns True if confidence meets or exceeds acceptance threshold."""
        return confidence_score >= cls.ACCEPT_THRESHOLD

    @classmethod
    def should_fail_closed(cls, confidence_score: int) -> bool:
        """Returns True if confidence is below minimum reliability threshold."""
        return confidence_score < cls.UNCERTAIN_THRESHOLD
