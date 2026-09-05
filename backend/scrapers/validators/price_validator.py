"""
Price Validator Module
======================
Validates mathematical relationships between current price, original price (MRP), and discount percentages.
"""
from typing import Optional, Tuple, Dict, Any


class PriceValidator:
    @classmethod
    def validate_prices(
        cls,
        current_price: Optional[float],
        original_price: Optional[float],
        extracted_discount: Optional[float] = None,
    ) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """
        Validate prices and compute/verify discount percentage.
        Returns: (verified_current_price, verified_original_price, verified_discount)
        """
        if current_price is None or current_price <= 0:
            return None, None, None

        verified_original: Optional[float] = None
        verified_discount: Optional[float] = None

        # MRP must be strictly greater than or equal to current price
        if original_price is not None and original_price >= current_price:
            verified_original = original_price

        # Calculate mathematical discount
        if verified_original is not None and verified_original > current_price:
            calc_discount = round(((verified_original - current_price) / verified_original) * 100.0)
            if 0 <= calc_discount <= 100:
                verified_discount = float(calc_discount)

        # Cross-verify with extracted discount if available
        if extracted_discount is not None and 0 <= extracted_discount <= 100:
            if verified_discount is None:
                verified_discount = float(extracted_discount)
            elif abs(verified_discount - extracted_discount) <= 2:  # within rounding tolerance
                verified_discount = float(extracted_discount)

        return current_price, verified_original, verified_discount

    @classmethod
    def is_price_spike_suspicious(cls, old_price: Optional[float], new_price: Optional[float]) -> bool:
        """
        Detect sudden extreme price drop (>50%) or spike (>300%) that warrants a re-verification fetch before triggering alerts.
        """
        if old_price is None or new_price is None or old_price <= 0 or new_price <= 0:
            return False

        # Drop by more than 50%
        if new_price < old_price * 0.50:
            return True

        # Spike by more than 300%
        if new_price > old_price * 3.0:
            return True

        return False
