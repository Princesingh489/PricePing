"""
PricePing Product Matching Engine
=================================
Executes the strict Product Identity -> Variant -> Availability -> Price Pipeline.
Enforces all 25 Core Rules:
- Rule 1: Never determine identity from title alone.
- Rule 2: Never invent GTIN/EAN/UPC.
- Rule 3: Retailer SKU is store-internal, not universal.
- Rule 4: Separate product identity from variant identity.
- Rules 5-10: Strict checks on size, color, storage, RAM, pack count, volume.
- Rules 11-12: Hard conflicts on brand and model.
- Rules 17-20: 3 Distinct States (Verified Match, Possible Match, No Verified Match).
- Rules 24-25: Expose match_reason and audit signals; prefer correct No Match over false match.
"""
import re
from typing import Optional, Dict, Any, List, Tuple
from services.product_normalizer import ProductNormalizer
from services.identifier_matcher import IdentifierMatcher
from services.variant_matcher import VariantMatcher
from services.availability_checker import AvailabilityChecker


class MatchResult(tuple):
    """
    Tuple supporting (is_match, confidence, reason) unpacking with structured attributes.
    """
    signals: Dict[str, Any]
    audit: Dict[str, Any]
    match_status: str

    def __new__(
        cls,
        is_match: bool,
        confidence: float,
        reason: str,
        signals: Dict[str, Any],
        audit: Optional[Dict[str, Any]] = None,
        match_status: Optional[str] = None,
    ):
        instance = super().__new__(cls, (is_match, confidence, reason))
        instance.signals = signals
        instance.audit = audit or {}
        instance.match_status = match_status or ("verified_match" if is_match else "no_verified_match")
        return instance

    @property
    def is_match(self) -> bool:
        return self[0]

    @property
    def confidence(self) -> float:
        return self[1]

    @property
    def reason(self) -> str:
        return self[2]


class ProductMatchingEngine:
    """Multi-stage deterministic product matching and variant verification engine."""

    STOPWORDS = {
        "with", "for", "the", "and", "in", "of", "to", "on", "a", "an", "is", "by",
        "phone", "smartphone", "edition", "online", "india", "at", "best", "price",
        "buy", "original", "genuine", "men", "mens", "men's", "women", "womens",
        "women's", "boys", "girls", "unisex"
    }

    ACCESSORY_TERMS = {
        "case", "cover", "cases", "covers", "tempered glass", "screen protector", "protector",
        "back cover", "flip cover", "skin", "skins", "cable", "cables", "charging cable",
        "charger", "chargers", "adapter", "adapters", "strap", "straps", "band", "bands",
        "ear tips", "eartips", "pouch", "pouches", "sleeve", "sleeves", "holder", "stand",
        "mount", "bumper"
    }

    @classmethod
    def is_accessory(cls, text: str) -> bool:
        lower = text.lower()
        return any(term in lower for term in cls.ACCESSORY_TERMS)

    @classmethod
    def calculate_token_similarity(cls, text1: str, text2: str) -> Tuple[float, float, float]:
        """Compute containment and Jaccard token overlap after normalization."""
        norm1 = ProductNormalizer.normalize_text(text1)
        norm2 = ProductNormalizer.normalize_text(text2)

        w1 = {w for w in norm1.split() if len(w) > 1 and w not in cls.STOPWORDS}
        w2 = {w for w in norm2.split() if len(w) > 1 and w not in cls.STOPWORDS}

        if not w1 or not w2:
            return 0.0, 0.0, 0.0

        overlap = w1.intersection(w2)
        containment = len(overlap) / min(len(w1), len(w2))
        jaccard = len(overlap) / len(w1.union(w2))
        combined = round(containment * 0.70 + jaccard * 0.30, 2)
        return combined, round(containment, 2), round(jaccard, 2)

    @classmethod
    def evaluate_candidate(
        cls,
        base_product: Dict[str, Any],
        candidate: Dict[str, Any],
        min_confidence_threshold: float = 0.90,
    ) -> MatchResult:
        """
        Evaluate candidate listing against base product using the full 25-Rule Pipeline.
        """
        base_title = base_product.get("title") or base_product.get("product_name") or ""
        cand_title = candidate.get("title") or candidate.get("product_name") or ""

        base_brand = base_product.get("brand")
        cand_brand = candidate.get("brand")

        # Extract structured attributes
        base_attrs = ProductNormalizer.extract_structured_attributes(
            base_title, brand=base_brand, description=base_product.get("description")
        )
        cand_attrs = ProductNormalizer.extract_structured_attributes(
            cand_title, brand=cand_brand, description=candidate.get("description")
        )

        # Merge any explicit overrides passed in dictionaries
        for k in ["color", "size", "storage", "ram", "model", "brand", "pack_count"]:
            if base_product.get(k):
                base_attrs[k] = base_product[k]
            if candidate.get(k):
                cand_attrs[k] = candidate[k]

        # Audit object tracking all criteria
        audit: Dict[str, Any] = {
            "brand_match": None,
            "model_match": None,
            "gtin_match": None,
            "color_match": None,
            "size_match": None,
            "storage_match": None,
            "ram_match": None,
            "title_similarity": 0.0,
            "variant_match": None,
            "match_confidence": 0.0,
            "match_reason": "Evaluating candidate",
        }

        signals: Dict[str, Any] = {
            "base_specs": base_attrs,
            "candidate_specs": cand_attrs,
            "hard_conflict": False,
        }

        # Helper to ensure audit signals are synchronized into signals dictionary
        def _make_result(is_match: bool, conf: float, reason: str, status: str) -> MatchResult:
            audit["match_confidence"] = conf
            audit["match_reason"] = reason
            combined_signals = dict(signals)
            combined_signals.update(audit)
            return MatchResult(is_match, conf, reason, combined_signals, audit, status)

        # ── STEP 1: Hard Reject — Anti-Accessory Discrimination ────────
        b_acc = cls.is_accessory(base_title)
        c_acc = cls.is_accessory(cand_title)
        if b_acc != c_acc:
            signals["hard_conflict"] = True
            signals["accessory_check"] = False
            signals["accessory_match"] = False
            return _make_result(False, 0.0, "Accessory mismatch: One item is an accessory, the other is a device", "no_verified_match")

        signals["accessory_check"] = True
        signals["accessory_match"] = True

        # ── STEP 2: Hard Reject — Brand Compatibility (Rule 12) ────────
        b_norm_b = ProductNormalizer.normalize_brand(base_attrs.get("brand"))
        c_norm_b = ProductNormalizer.normalize_brand(cand_attrs.get("brand"))

        if b_norm_b:
            if c_norm_b and b_norm_b != c_norm_b:
                audit["brand_match"] = False
                signals["hard_conflict"] = True
                return _make_result(False, 0.0, f"Brand conflict: '{b_norm_b}' != '{c_norm_b}'", "no_verified_match")
            if not c_norm_b and b_norm_b not in cand_title.lower():
                audit["brand_match"] = False
                signals["hard_conflict"] = True
                return _make_result(False, 0.0, f"Candidate missing required brand '{b_norm_b}'", "no_verified_match")
            audit["brand_match"] = True
        else:
            audit["brand_match"] = True

        # ── STEP 3: Identifier Matching (GTIN, MPN, Model) (Rule 2) ───
        base_ids = {
            "gtin": base_product.get("gtin") or base_product.get("ean") or base_product.get("upc"),
            "mpn": base_product.get("mpn"),
            "model": base_attrs.get("model"),
        }
        cand_ids = {
            "gtin": candidate.get("gtin") or candidate.get("ean") or candidate.get("upc"),
            "mpn": candidate.get("mpn"),
            "model": cand_attrs.get("model"),
        }
        is_id_compat, id_boost, id_reason, id_signals = IdentifierMatcher.match_identifiers(base_ids, cand_ids)

        if not is_id_compat:
            audit["gtin_match"] = id_signals.get("gtin_match")
            audit["model_match"] = id_signals.get("model_match")
            signals["hard_conflict"] = True
            return _make_result(False, 0.0, id_reason or "Identifier conflict", "no_verified_match")

        audit["gtin_match"] = id_signals.get("gtin_match")
        audit["model_match"] = id_signals.get("model_match")

        # ── STEP 4: Hard Reject — Model Code Mismatch (Rule 11) ────────
        b_model = base_attrs.get("model")
        c_model = cand_attrs.get("model")
        if b_model and c_model and b_model.lower() != c_model.lower():
            audit["model_match"] = False
            signals["hard_conflict"] = True
            return _make_result(False, 0.0, f"Model conflict: '{b_model}' != '{c_model}'", "no_verified_match")
        if b_model and not c_model:
            b_tokens = [w for w in b_model.lower().split() if w]
            if not all(w in cand_title.lower() for w in b_tokens):
                audit["model_match"] = False
                signals["hard_conflict"] = True
                return _make_result(False, 0.0, f"Candidate missing model identifier '{b_model}'", "no_verified_match")
            audit["model_match"] = True
        elif b_model and c_model:
            audit["model_match"] = True

        # ── STEP 5: Variant Matching & Hard Conflict Check (Rules 4-10) 
        is_var_match, var_reason, var_signals = VariantMatcher.match_variants(base_attrs, cand_attrs)
        audit["size_match"] = var_signals.get("size_match")
        audit["color_match"] = var_signals.get("color_match")
        audit["storage_match"] = var_signals.get("storage_match")
        audit["ram_match"] = var_signals.get("ram_match")
        audit["variant_match"] = is_var_match

        if not is_var_match:
            signals["hard_conflict"] = True
            return _make_result(False, 0.0, var_reason, "no_verified_match")

        # ── STEP 6: Token Similarity & Containment (Step 20 Scoring) ──
        sim_score, containment, jaccard = cls.calculate_token_similarity(base_title, cand_title)
        audit["title_similarity"] = sim_score

        # ── STEP 7: Evidence Scoring Matrix (Steps 20, 21, 23, 48) ────
        # Deterministic hierarchy:
        # Level 1 — GTIN/EAN/UPC exact match (+50)
        # Level 2 — Brand (+25-30) + MPN/Model (+15-25)
        # Level 3 — Exact Variant (+25-35)
        # Level 4 — Attribute & Title token containment (+15-35)
        total_score = 0.0

        if audit["gtin_match"] is True:
            # Identifier-dominated branch (Step 4, 21)
            total_score += 50.0
            if audit["brand_match"] is True:
                total_score += 20.0
            if is_var_match:
                total_score += 20.0
            if containment >= 0.50:
                total_score += 10.0
        else:
            # Attribute-dominated branch (Step 23, 48)
            if audit["brand_match"] is True:
                total_score += 30.0
            if is_var_match:
                total_score += 35.0
            if audit["model_match"] is True:
                total_score += 25.0

            # Title & attribute token containment
            if containment >= 0.75:
                total_score += 35.0
            elif containment >= 0.60:
                total_score += 20.0
            elif containment >= 0.50:
                total_score += 10.0

        # High model match with high containment achieves 95+ score
        if audit["model_match"] and containment >= 0.80:
            total_score = max(total_score, 95.0)

        # Normalize confidence to 0.0 - 1.0 scale
        confidence = min(round(total_score / 100.0, 2), 1.0)


        # ── STEP 8: Decision Thresholds (Step 49) ──────────────────────
        if confidence >= min_confidence_threshold and is_var_match:
            reason = "✓ Verified exact product and variant match"
            if audit["gtin_match"]:
                reason += f" (GTIN: {base_ids['gtin']})"
            elif audit["model_match"]:
                reason += f" (Model: {b_model or c_model})"
            return _make_result(True, confidence, reason, "verified_match")

        if confidence >= 0.75:
            reason = "? Possible match (Product looks similar, verification inconclusive)"
            return _make_result(False, confidence, reason, "possible_match")

        reason = f"— No verified match found (Confidence {confidence:.2f} < threshold {min_confidence_threshold:.2f})"
        return _make_result(False, confidence, reason, "no_verified_match")
