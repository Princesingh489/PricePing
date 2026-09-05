"""
PricePing Exact Variant Price Extractor
=======================================
Ensures extracted price precisely corresponds to the selected active variant
(e.g., Size 32, 256GB Black) rather than a generic parent page default or minimum.
"""
from typing import Optional, Dict, Any, List, Tuple
from services.product_normalizer import ProductNormalizer


class PriceExtractor:
    """Extracts and verifies prices for exact product variants."""

    @staticmethod
    def extract_variant_price(
        default_price: Optional[float],
        default_mrp: Optional[float],
        variants: Optional[List[Dict[str, Any]]],
        target_variant: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """
        Extract selling price, MRP, and discount percentage for target variant.
        Returns:
            (current_price: Optional[float], original_price: Optional[float], discount_percentage: Optional[float])
        """
        if not variants or not target_variant:
            discount = None
            if default_price and default_mrp and default_mrp > default_price:
                discount = round(((default_mrp - default_price) / default_mrp) * 100, 1)
            return default_price, default_mrp, discount

        target_size = ProductNormalizer.normalize_size(target_variant.get("size"))
        target_color = ProductNormalizer.normalize_color(target_variant.get("color"))

        # Look for matching variant in variants list
        for v in variants:
            v_size = ProductNormalizer.normalize_size(v.get("size") or v.get("name"))
            v_color = ProductNormalizer.normalize_color(v.get("color"))

            size_matches = True
            if target_size and v_size:
                size_matches = (target_size == v_size)

            color_matches = True
            if target_color and v_color:
                color_matches = (target_color == v_color)

            if size_matches and color_matches:
                v_price = v.get("price")
                v_mrp = v.get("mrp") or default_mrp or v_price
                if v_price is not None:
                    curr_p = float(v_price)
                    orig_p = float(v_mrp) if v_mrp else curr_p
                    disc = round(((orig_p - curr_p) / orig_p) * 100, 1) if orig_p > curr_p else None
                    return curr_p, orig_p, disc

        # Fallback to defaults
        discount = None
        if default_price and default_mrp and default_mrp > default_price:
            discount = round(((default_mrp - default_price) / default_mrp) * 100, 1)
        return default_price, default_mrp, discount
