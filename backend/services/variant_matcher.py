"""
PricePing Variant Matcher
=========================
Evaluates variant attributes:
- Apparel & Footwear sizes
- Colors & Shades
- Electronics Storage & RAM
- Pack counts & fluid volumes
Enforces Rule 4: Separate product identity from variant identity.
Enforces Rule 5-10: Hard-reject conflicts in size, color, storage, RAM, pack count, and volume.
"""
from typing import Optional, Dict, Any, Tuple
from services.product_normalizer import ProductNormalizer


class VariantMatcher:
    """Evaluates exact match across physical variant dimensions with zero-tolerance conflict rejection."""

    @classmethod
    def match_variants(
        cls,
        base_variant: Dict[str, Any],
        candidate_variant: Dict[str, Any],
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Compare variants between base product and candidate.
        Returns:
            (is_exact_match: bool, reason: str, signals: Dict[str, Any])
        """
        signals = {
            "size_match": True,
            "color_match": True,
            "storage_match": True,
            "ram_match": True,
            "pack_match": True,
            "volume_match": True,
            "variant_conflict": False,
        }

        # 1. Size Check (Apparel, Footwear, Waist)
        b_size = ProductNormalizer.normalize_size(base_variant.get("size"))
        c_size = ProductNormalizer.normalize_size(candidate_variant.get("size"))

        if b_size and c_size:
            if b_size != c_size:
                signals["size_match"] = False
                signals["variant_conflict"] = True
                return False, f"Size variant mismatch: Base '{b_size}' vs Candidate '{c_size}'", signals
        elif b_size and not c_size:
            # If base specifically requires a size, candidate variant must be verified
            signals["size_match"] = False
            signals["variant_conflict"] = True
            return False, f"Target size '{b_size}' not confirmed on candidate listing", signals

        # 2. Color Check
        b_color = ProductNormalizer.normalize_color(base_variant.get("color"))
        c_color = ProductNormalizer.normalize_color(candidate_variant.get("color"))

        if b_color and c_color:
            if b_color != c_color:
                signals["color_match"] = False
                signals["variant_conflict"] = True
                return False, f"Color variant mismatch: Base '{b_color}' vs Candidate '{c_color}'", signals

        # 3. Storage Check (Critical for Electronics)
        b_storage = ProductNormalizer.normalize_storage(base_variant.get("storage"))
        c_storage = ProductNormalizer.normalize_storage(candidate_variant.get("storage"))

        if b_storage and c_storage:
            if b_storage != c_storage:
                signals["storage_match"] = False
                signals["variant_conflict"] = True
                return False, f"Storage variant mismatch: Base '{b_storage}' vs Candidate '{c_storage}'", signals
        elif b_storage and not c_storage:
            signals["storage_match"] = False
            signals["variant_conflict"] = True
            return False, f"Target storage capacity '{b_storage}' not confirmed on candidate", signals

        # 4. RAM Check (Critical for Electronics)
        b_ram = ProductNormalizer.normalize_ram(base_variant.get("ram"))
        c_ram = ProductNormalizer.normalize_ram(candidate_variant.get("ram"))

        if b_ram and c_ram:
            if b_ram != c_ram:
                signals["ram_match"] = False
                signals["variant_conflict"] = True
                return False, f"RAM variant mismatch: Base '{b_ram}' vs Candidate '{c_ram}'", signals

        # 5. Pack Count Check
        b_pack = base_variant.get("pack_count") or 1
        c_pack = candidate_variant.get("pack_count") or 1

        if b_pack != c_pack:
            signals["pack_match"] = False
            signals["variant_conflict"] = True
            return False, f"Pack count mismatch: Base {b_pack} pcs vs Candidate {c_pack} pcs", signals

        # 6. Fluid Volume / Weight Check
        b_vol = base_variant.get("volume")
        c_vol = candidate_variant.get("volume")

        if b_vol and c_vol:
            if b_vol != c_vol:
                signals["volume_match"] = False
                signals["variant_conflict"] = True
                return False, f"Volume/weight mismatch: Base '{b_vol}' vs Candidate '{c_vol}'", signals

        return True, "Exact variant match confirmed", signals
