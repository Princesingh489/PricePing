"""
PricePing Availability & Multi-Store Status Checker
===================================================
Evaluates stock availability independently from product and variant identity.
Calculates 5-store aggregated availability metrics (Steps 18, 39, 40).
"""
from typing import List, Dict, Any


class AvailabilityChecker:
    """Evaluates availability status and calculates cross-store purchase readiness."""

    @staticmethod
    def evaluate_offer_status(
        is_product_matched: bool,
        is_variant_matched: bool,
        confidence: float,
        is_in_stock: bool,
        has_hard_conflict: bool,
    ) -> Dict[str, Any]:
        """
        Derive standardized match status and UI display labels.
        States:
        1. verified_match: Product confirmed + variant confirmed + no conflicts + confidence >= 0.90
        2. possible_match: Confidence 0.75 - 0.89, no hard conflict
        3. no_verified_match: Confidence < 0.75 or hard conflict
        """
        if has_hard_conflict:
            return {
                "match_status": "no_verified_match",
                "availability": "unavailable",
                "badge_label": "— No Verified Match",
                "is_purchasable": False,
            }

        if is_product_matched and is_variant_matched and confidence >= 0.90:
            if is_in_stock:
                return {
                    "match_status": "verified_match",
                    "availability": "in_stock",
                    "badge_label": "✓ Verified Match",
                    "is_purchasable": True,
                }
            else:
                return {
                    "match_status": "verified_match",
                    "availability": "out_of_stock",
                    "badge_label": "✓ Verified Match (Out of Stock)",
                    "is_purchasable": False,
                }

        if is_product_matched and confidence >= 0.75:
            return {
                "match_status": "possible_match",
                "availability": "in_stock" if is_in_stock else "out_of_stock",
                "badge_label": "? Possible Match",
                "is_purchasable": False,
            }

        return {
            "match_status": "no_verified_match",
            "availability": "unavailable",
            "badge_label": "— No Verified Match",
            "is_purchasable": False,
        }

    @staticmethod
    def calculate_five_stores_summary(stores: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate if product is available across all 5 stores.
        Enforces Step 39 & Step 40.
        """
        total_stores = len(stores) if stores else 5
        verified_stores = [s for s in stores if s.get("match_status") in ("verified_match", "current_store")]
        in_stock_stores = [s for s in verified_stores if s.get("availability") == "in_stock"]

        verified_count = len(verified_stores)
        in_stock_count = len(in_stock_stores)
        is_all_available = (in_stock_count >= 5)

        if is_all_available:
            summary_text = f"🔥 Available on all {total_stores} stores"
        elif in_stock_count > 1:
            summary_text = f"Available on {in_stock_count} of {total_stores} stores"
        elif in_stock_count == 1:
            summary_text = f"Available on 1 of {total_stores} stores"
        elif verified_count > 0:
            summary_text = f"Same product found on {verified_count} stores, but currently Out of Stock"
        else:
            summary_text = "No verified matches found on other stores"

        status = "all_available" if is_all_available else ("partially_available" if in_stock_count > 0 else "unavailable")
        return {
            "all_available": is_all_available,
            "is_available_all_5": is_all_available,
            "available_count": in_stock_count,
            "in_stock_count": in_stock_count,
            "verified_match_count": verified_count,
            "verified_count": verified_count,
            "total_stores": total_stores,
            "message": summary_text,
            "summary_text": summary_text,
            "status": status,
        }

