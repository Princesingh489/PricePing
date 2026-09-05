"""
PricePing Product Identifier Matcher
====================================
Deterministic evaluation of manufacturer-assigned product identifiers:
- Level 1: GTIN / EAN / UPC (Cross-retailer universal proof)
- Level 2: MPN / Manufacturer Model Number
- Level 3: Retailer-internal SKUs (ASIN, FSN, PID, Style ID)
Enforces Rule 2: Never invent or guess GTINs.
Enforces Rule 3: Retailer SKU is store-internal, not universal.
"""
import re
from typing import Optional, Dict, Any, Tuple


class IdentifierMatcher:
    """Evaluates universal and manufacturer identifiers across marketplace products."""

    @staticmethod
    def clean_gtin(gtin: Optional[str]) -> Optional[str]:
        """Strip non-numeric characters and validate standard GTIN/EAN length (8, 12, 13, 14 digits)."""
        if not gtin:
            return None
        cleaned = re.sub(r'[^\d]', '', str(gtin).strip())
        if len(cleaned) in (8, 12, 13, 14):
            return cleaned
        return None

    @staticmethod
    def clean_model_code(code: Optional[str]) -> Optional[str]:
        """Normalize MPN or model code for whitespace and non-alphanumeric variance."""
        if not code:
            return None
        cleaned = re.sub(r'[^a-zA-Z0-9]', '', str(code).lower().strip())
        return cleaned if len(cleaned) >= 2 else None

    @classmethod
    def match_identifiers(
        cls,
        base_identifiers: Dict[str, Any],
        candidate_identifiers: Dict[str, Any],
    ) -> Tuple[bool, float, Optional[str], Dict[str, Any]]:
        """
        Compare identifiers between base product and candidate listing.
        Returns:
            (is_compatible: bool, score_boost: float, reason: Optional[str], signals: Dict[str, Any])
        """
        signals = {
            "gtin_match": None,
            "mpn_match": None,
            "model_match": None,
            "hard_conflict": False,
        }

        # 1. Level 1: GTIN / EAN / UPC Comparison
        base_gtin = cls.clean_gtin(base_identifiers.get("gtin") or base_identifiers.get("ean") or base_identifiers.get("upc"))
        cand_gtin = cls.clean_gtin(candidate_identifiers.get("gtin") or candidate_identifiers.get("ean") or candidate_identifiers.get("upc"))

        if base_gtin and cand_gtin:
            if base_gtin == cand_gtin:
                signals["gtin_match"] = True
                return True, 50.0, f"Verified GTIN/EAN Exact Match ({base_gtin})", signals
            else:
                signals["gtin_match"] = False
                signals["hard_conflict"] = True
                return False, 0.0, f"GTIN conflict: {base_gtin} != {cand_gtin}", signals

        # 2. Level 2: MPN / Manufacturer Model Number Comparison
        base_mpn = cls.clean_model_code(base_identifiers.get("mpn") or base_identifiers.get("model_number"))
        cand_mpn = cls.clean_model_code(candidate_identifiers.get("mpn") or candidate_identifiers.get("model_number"))

        if base_mpn and cand_mpn:
            if base_mpn == cand_mpn:
                signals["mpn_match"] = True
                return True, 25.0, f"Verified MPN/Model Number Exact Match ({base_mpn})", signals
            else:
                signals["mpn_match"] = False
                signals["hard_conflict"] = True
                return False, 0.0, f"MPN conflict: {base_mpn} != {cand_mpn}", signals

        # 3. Model Code / Line Comparison
        base_model = cls.clean_model_code(base_identifiers.get("model"))
        cand_model = cls.clean_model_code(candidate_identifiers.get("model"))

        if base_model and cand_model:
            if base_model == cand_model:
                signals["model_match"] = True
                return True, 15.0, f"Verified Product Model Match ({base_model})", signals
            else:
                signals["model_match"] = False
                signals["hard_conflict"] = True
                return False, 0.0, f"Model conflict: {base_model} != {cand_model}", signals

        # Neutral: Identifiers not available on both sides
        return True, 0.0, None, signals
