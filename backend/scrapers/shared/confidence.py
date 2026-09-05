"""
Shared Confidence & Validation Engine
======================================
Scores candidate evidence field-by-field, computes overall confidence, verifies mathematical discounts,
and decides whether to fast-accept or fail-closed.
"""
from typing import Optional, List, Tuple, Dict, Any
from scrapers.shared.models import PriceCandidate, FieldConfidence


class ConfidenceEngine:
    CONFIDENCE_THRESHOLD = 70
    FAIL_CLOSED_THRESHOLD = 70
    OVERALL_VERIFIED_THRESHOLD = 70
    FAST_ACCEPT_PRICE_CONFIDENCE = 90
    FAST_ACCEPT_TITLE_CONFIDENCE = 85
    FAST_ACCEPT_IMAGE_CONFIDENCE = 80

    @classmethod
    def evaluate(
        cls,
        store: Any,
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
        availability: Any,
        original_price: Optional[float] = None,
        debug_info: Optional[Any] = None,
    ) -> Tuple[int, str, List[str]]:
        """
        Calculates score and returns (score, status, warnings).
        Status values: 'verified' (score >= 70), 'needs_verification' (score < 70), 'extraction_failed'.
        """
        score = 0
        warnings = []

        # 1. Store detection (+10)
        if store and str(store) != "unknown":
            score += 10
        else:
            warnings.append("Store could not be reliably identified")

        # 2. Product ID validation (+20)
        if product_id and len(str(product_id).strip()) >= 3:
            score += 20
        else:
            warnings.append("Exact store product identifier (ASIN/PID) missing or invalid")

        # 3. Product Title validation (+20)
        if selected_title and len(str(selected_title).strip()) >= 5:
            score += 20
            if len(candidate_titles) > 1:
                t1 = str(selected_title).lower()
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
            score += 15
            valid_prices = [p["value"] for p in candidate_prices if p.get("value") and isinstance(p["value"], (int, float))]
            if len(valid_prices) >= 2:
                matching_prices = [p for p in valid_prices if abs(p - selected_price) <= 1.0]
                if len(matching_prices) >= 2:
                    score += 10
                elif price_source and "main_container" in str(price_source):
                    score += 10
            elif price_source and "main_container" in str(price_source):
                score += 10

            if original_price and original_price < selected_price:
                warnings.append("Original price is lower than current selling price")
        else:
            warnings.append("Current selling price could not be determined")

        # 5. Main Image validation (+15)
        if selected_image and str(selected_image).startswith("http"):
            score += 15
        else:
            warnings.append("Main product image could not be verified")

        # 6. Availability confirmation (+10)
        if availability and str(availability) != "unknown":
            score += 10
        else:
            if score >= 60:
                score += 5

        score = max(0, min(100, score))

        if score >= cls.CONFIDENCE_THRESHOLD and selected_price and selected_title:
            status = "verified"
        elif selected_price or selected_title:
            status = "needs_verification"
        else:
            status = "extraction_failed"

        return score, status, warnings

    @classmethod
    def calculate_field_confidence(
        cls,
        selected_price: Optional[float],
        price_candidates: List[PriceCandidate],
        has_main_container: bool,
        has_title: bool,
        has_image: bool,
        json_ld_price: Optional[float] = None,
        original_price: Optional[float] = None,
        discount_percentage: Optional[float] = None,
        rating: Optional[float] = None,
        variant: Optional[Dict[str, str]] = None,
        is_buybox_active: bool = True,
    ) -> FieldConfidence:
        """
        Calculate individual confidence scores (0-100) for all product fields.
        """
        # 1. Price Confidence
        price_score = 0
        if selected_price is not None and selected_price > 0:
            price_score = 50  # base valid price

            if has_main_container:
                price_score += 25
            else:
                price_score += 15

            # Agreement with JSON-LD
            if json_ld_price is not None and abs(json_ld_price - selected_price) < 1.0:
                price_score += 20

            # Multiple candidate consensus
            matching_candidates = [
                c for c in price_candidates
                if c.category in ("selling_price", "main_dom") and abs(c.value - selected_price) < 1.0
            ]
            if len(matching_candidates) >= 2:
                price_score += 10

            # Mathematical discount verification bonus
            if original_price and original_price > selected_price:
                calc_discount = round(((original_price - selected_price) / original_price) * 100)
                if discount_percentage and abs(calc_discount - discount_percentage) <= 2:
                    price_score += 10

            price_score = min(price_score, 100)

        # 2. Title Confidence
        title_score = 95 if has_title and has_main_container else (85 if has_title else 0)

        # 3. Image Confidence
        image_score = 90 if has_image and has_main_container else (80 if has_image else 0)

        # 4. Original Price & Discount Confidence
        original_price_score = 90 if (original_price and original_price >= (selected_price or 0)) else 0
        discount_score = 90 if discount_percentage is not None else 0

        # 5. Rating Confidence
        rating_score = 90 if rating is not None and (0.0 <= rating <= 5.0) else 0

        # 6. Variant Confidence
        variant_score = 95 if variant and len(variant) > 0 else 85

        # 7. Stock Confidence
        stock_score = 95 if is_buybox_active else 80

        # 8. Overall Confidence (Weighted Average)
        overall = int(round(
            (price_score * 0.35) +
            (title_score * 0.25) +
            (image_score * 0.15) +
            (variant_score * 0.10) +
            (stock_score * 0.05) +
            ((original_price_score or price_score) * 0.05) +
            ((rating_score or 70) * 0.05)
        ))
        overall = min(max(overall, 0), 100)

        return FieldConfidence(
            title=title_score,
            current_price=price_score,
            original_price=original_price_score,
            discount=discount_score,
            image=image_score,
            rating=rating_score,
            variant=variant_score,
            stock=stock_score,
            overall=overall,
        )

    @classmethod
    def can_fast_accept(cls, field_conf: FieldConfidence, conflicts_exist: bool = False) -> bool:
        """
        Fast Acceptance Rule:
        If Title >= 85, Price >= 90, Image >= 80 with no critical conflicts,
        accept immediately without launching Playwright browser.
        """
        if conflicts_exist:
            return False
        return (
            field_conf.current_price >= cls.FAST_ACCEPT_PRICE_CONFIDENCE
            and field_conf.title >= cls.FAST_ACCEPT_TITLE_CONFIDENCE
            and field_conf.image >= cls.FAST_ACCEPT_IMAGE_CONFIDENCE
        )

    @classmethod
    def should_fail_closed(cls, confidence_score: int) -> bool:
        """Fail-closed if confidence is below 70."""
        return confidence_score < cls.FAIL_CLOSED_THRESHOLD

    @classmethod
    def validate_and_calculate_discount(
        cls,
        current_price: Optional[float],
        original_price: Optional[float],
        extracted_discount: Optional[float] = None,
    ) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
        """
        Validates MRP > Price and calculates/verifies discount percentage and amount saved.
        Returns: (current_price, original_price, discount_percentage, saved_amount)
        """
        if current_price is None or current_price <= 0:
            return None, None, None, None

        if original_price is None or original_price <= 0 or original_price <= current_price:
            if extracted_discount is not None and 0 < extracted_discount < 100:
                # Derive MRP from verified current price and official on-page discount
                derived_mrp = float(round(current_price / (1.0 - (extracted_discount / 100.0))))
                if derived_mrp > current_price:
                    original_price = derived_mrp
                    saved_amount = float(round(original_price - current_price, 2))
                    return current_price, original_price, float(extracted_discount), saved_amount
            return current_price, None, None, None

        saved_amount = float(round(original_price - current_price, 2))
        calculated_discount = float(round(((original_price - current_price) / original_price) * 100))

        verified_discount = calculated_discount
        if extracted_discount is not None and 0 <= extracted_discount <= 100:
            if abs(calculated_discount - extracted_discount) <= 3:
                verified_discount = float(extracted_discount)

        return current_price, original_price, verified_discount, saved_amount
