import logging
from typing import Optional, List, Dict, Any
from db.models import PlatformEnum, AvailabilityEnum
from scrapers.base_scraper import ExtractionResult, ExtractionDebug

logger = logging.getLogger(__name__)


class ConfidenceEngine:
    """
    Evaluates extracted candidate data and computes a 0-100 confidence score
    based on multi-source agreement, container validation, and identifier integrity.
    """

    CONFIDENCE_THRESHOLD = 70

    @classmethod
    def evaluate(
        cls,
        store: PlatformEnum,
        product_id: Optional[str],
        selected_title: Optional[str],
        title_source: Optional[str],
        candidate_titles: List[Dict[str, Any]],
        selected_price: Optional[float],
        price_source: Optional[str],
        candidate_prices: List[Dict[str, Any]],
        selected_image: Optional[str],
        image_source: Optional[str],
        candidate_images: List[Dict[str, Any]],
        availability: AvailabilityEnum,
        original_price: Optional[float] = None,
        debug_info: Optional[ExtractionDebug] = None,
    ) -> tuple[int, str, List[str]]:
        """
        Calculates score and returns (score, status, warnings).
        Status values: 'verified' (score >= 70), 'needs_verification' (score < 70), 'extraction_failed'.
        """
        score = 0
        warnings = []

        # 1. Store detection (+10)
        if store and store != PlatformEnum.unknown:
            score += 10
        else:
            warnings.append("Store could not be reliably identified")

        # 2. Product ID validation (+20)
        if product_id and len(product_id.strip()) >= 3:
            score += 20
        else:
            warnings.append("Exact store product identifier (ASIN/PID) missing or invalid")

        # 3. Product Title validation (+20)
        if selected_title and len(selected_title.strip()) >= 5:
            score += 20
            # Bonus: Title matches multiple candidate sources
            if len(candidate_titles) > 1:
                # Check if JSON-LD and DOM title agree
                t1 = selected_title.lower()
                matching_sources = [
                    c for c in candidate_titles
                    if c.get("value") and any(w in str(c["value"]).lower() for w in t1.split()[:3])
                ]
                if len(matching_sources) >= 2:
                    score = min(100, score + 5)
        else:
            warnings.append("Main product title could not be identified")

        # 4. Current Price validation (+25)
        if selected_price and selected_price > 0:
            score += 15  # Base price found

            # Multi-source price agreement (+10)
            valid_prices = [p["value"] for p in candidate_prices if p.get("value") and isinstance(p["value"], (int, float))]
            if len(valid_prices) >= 2:
                # Check if multiple sources report the same or very close price
                matching_prices = [p for p in valid_prices if abs(p - selected_price) <= 1.0]
                if len(matching_prices) >= 2:
                    score += 10
                elif price_source and "main_container" in price_source:
                    score += 10
            elif price_source and "main_container" in price_source:
                score += 10

            # Sanity check: price vs original_price
            if original_price and original_price < selected_price:
                warnings.append("Original price is lower than current selling price")
        else:
            warnings.append("Current selling price could not be determined")

        # 5. Main Image validation (+15)
        if selected_image and selected_image.startswith("http"):
            score += 15
        else:
            warnings.append("Main product image could not be verified")

        # 6. Availability confirmation (+10)
        if availability and availability != AvailabilityEnum.unknown:
            score += 10
        else:
            # Default to in_stock if price and title are solid
            if score >= 60:
                score += 5

        # Clamp score between 0 and 100
        score = max(0, min(100, score))

        # Determine status
        if score >= cls.CONFIDENCE_THRESHOLD and selected_price and selected_title:
            status = "verified"
        elif selected_price or selected_title:
            status = "needs_verification"
        else:
            status = "extraction_failed"

        return score, status, warnings
