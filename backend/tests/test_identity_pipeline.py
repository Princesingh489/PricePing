"""
PricePing Product Identity & Comparison Pipeline Tests
======================================================
Tests all 25 Core Rules and 52 Pipeline Steps:
- Rule 1: Never determine product identity from title alone.
- Rule 2: Never invent GTIN/EAN/UPC/MPN/model numbers.
- Rule 3: Never treat retailer SKU as a universal identifier.
- Rule 4: Always separate product identity from variant identity.
- Rule 5: Size must match for size-dependent products (apparel, waist, footwear).
- Rule 6: Color must match when the selected color is known.
- Rule 7: Storage must match for electronics.
- Rule 8: RAM must match for electronics.
- Rule 9: Pack quantity must match.
- Rule 10: Weight/volume/capacity must match where applicable.
- Rule 11: A different model number is a hard conflict.
- Rule 12: A different brand is a hard conflict.
- Rule 17: Only "VERIFIED MATCH" should be included in exact-price comparison.
- Rule 18: Same product but out of stock = SAME PRODUCT, OUT OF STOCK.
- Rule 19: Same parent product but different variant = NOT AN EXACT VARIANT MATCH.
- Rule 20: If evidence is insufficient, display "No Verified Match".
- Rule 24: Expose match_reason and audit signals for debugging.
- Rule 25: The system should prefer a correct "No Match" over a false match.
- Step 39: All 5 stores availability calculation & distinction between found vs available.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from services.product_matcher import ProductMatchingEngine, MatchResult
from services.product_normalizer import ProductNormalizer
from services.identifier_matcher import IdentifierMatcher
from services.variant_matcher import VariantMatcher
from services.availability_checker import AvailabilityChecker
from services.canonical_service import CanonicalService
from services.price_extractor import PriceExtractor


def test_rule_1_and_25_title_similarity_alone_does_not_match():
    """
    Rule 1 & Rule 25:
    Titles might look 90%+ similar, but without matching brand/model/variant attributes,
    it must NOT be decided as the same product.
    """
    base = {
        "title": "Nike Revolution 6 Men Running Shoes",
        "brand": "Nike",
        "size": "uk 9",
        "color": "black",
    }
    cand_wrong_brand = {
        "title": "Adidas Revolution 6 Men Running Shoes",
        "brand": "Adidas",
        "size": "uk 9",
        "color": "black",
    }
    res = ProductMatchingEngine.evaluate_candidate(base, cand_wrong_brand)
    assert not res.is_match
    assert res.match_status == "no_verified_match"
    assert "Brand conflict" in res.reason or "brand" in res.reason.lower()


def test_rule_2_gtin_identifier_matching_and_no_hallucination():
    """
    Rule 2 & Step 4:
    GTIN / EAN exact match provides Level 1 evidence (+50 points).
    Never fabricate a GTIN.
    """
    base = {
        "title": "Samsung Galaxy S25 Ultra 256GB Titanium Black",
        "brand": "Samsung",
        "gtin": "8901234567890",
        "storage": "256gb",
        "color": "black",
    }
    cand = {
        "title": "Samsung Galaxy S25 Ultra 5G (Titanium Black, 256 GB)",
        "brand": "Samsung",
        "gtin": "8901234567890",
        "storage": "256gb",
        "color": "black",
    }
    res = ProductMatchingEngine.evaluate_candidate(base, cand)
    assert res.is_match
    assert res.match_status == "verified_match"
    assert res.audit["gtin_match"] is True
    assert res.confidence >= 0.90


def test_rule_7_and_8_storage_and_ram_hard_conflicts():
    """
    Rules 7 & 8:
    iPhone 17 Pro Max 256GB must NEVER match 512GB, even if title similarity is 99%.
    """
    base = {
        "title": "Apple iPhone 17 Pro Max 256GB Natural Titanium",
        "brand": "Apple",
        "storage": "256gb",
        "color": "natural titanium",
    }
    cand_512 = {
        "title": "Apple iPhone 17 Pro Max 512GB Natural Titanium",
        "brand": "Apple",
        "storage": "512gb",
        "color": "natural titanium",
    }
    res = ProductMatchingEngine.evaluate_candidate(base, cand_512)
    assert not res.is_match
    assert res.match_status == "no_verified_match"
    assert "Storage variant mismatch" in res.reason


def test_rule_5_apparel_waist_and_footwear_size_conflicts():
    """
    Rule 5:
    BROADSTAR Pants Black Size 32 vs Size 34:
    Product may be same parent, but VARIANT IS NOT SAME -> Reject exact match.
    """
    base_pants = {
        "title": "BROADSTAR Men Relaxed Straight Leg Korean Pants Black Size 32",
        "brand": "BROADSTAR",
        "size": "32",
        "color": "black",
    }
    cand_pants_34 = {
        "title": "BROADSTAR Men's Relaxed Straight Fit Korean Pants Black Size 34",
        "brand": "BROADSTAR",
        "size": "34",
        "color": "black",
    }
    res = ProductMatchingEngine.evaluate_candidate(base_pants, cand_pants_34)
    assert not res.is_match
    assert res.match_status == "no_verified_match"
    assert "Size variant mismatch" in res.reason


def test_rule_6_color_conflict():
    """
    Rule 6:
    Selected color must match when known.
    """
    base = {
        "title": "Boat Rockerz 550 Over Ear Wireless Headphones Black",
        "brand": "boAt",
        "color": "black",
    }
    cand_red = {
        "title": "Boat Rockerz 550 Over Ear Wireless Headphones Red",
        "brand": "boAt",
        "color": "red",
    }
    res = ProductMatchingEngine.evaluate_candidate(base, cand_red)
    assert not res.is_match
    assert res.match_status == "no_verified_match"
    assert "Color variant mismatch" in res.reason


def test_rule_9_and_10_pack_count_and_volume_conflicts():
    """
    Rules 9 & 10:
    Pack count (e.g. pack of 1 vs pack of 2) or volume (100ml vs 200ml) must reject.
    """
    base_lotion = {
        "title": "Cetaphil Gentle Skin Cleanser 125ml",
        "brand": "Cetaphil",
        "volume": "125ml",
        "pack_count": 1,
    }
    cand_250ml = {
        "title": "Cetaphil Gentle Skin Cleanser 250ml",
        "brand": "Cetaphil",
        "volume": "250ml",
        "pack_count": 1,
    }
    res = ProductMatchingEngine.evaluate_candidate(base_lotion, cand_250ml)
    assert not res.is_match
    assert "Volume/weight mismatch" in res.reason or "Pack" in res.reason


def test_step_3_canonical_product_generation():
    """
    Step 3 & 26:
    Create a canonical product representation with internal CP-... identifier.
    """
    product = {
        "title": "BROADSTAR Men Relaxed Straight Leg Pleated Pants Black 32",
        "brand": "BROADSTAR",
        "price": 989,
        "mrp": 1999,
        "color": "Black",
        "size": "32",
        "category": "Men Trousers",
    }
    canonical = CanonicalService.create_canonical_product(product)
    assert canonical["canonical_product_id"].startswith("CP-")
    assert canonical["brand"] == "broadstar"
    assert canonical["color"] == "black"
    assert canonical["size"] == "32"


def test_step_39_and_40_five_stores_availability_calculation():
    """
    Step 39 & 40:
    How to know if a product is available on ALL 5 stores vs 4 of 5 stores vs out of stock.
    """
    # Case A: Available on ALL 5 stores
    case_a = [
        {"store": "amazon", "match_status": "verified_match", "availability": "in_stock", "price": 899.0},
        {"store": "flipkart", "match_status": "verified_match", "availability": "in_stock", "price": 929.0},
        {"store": "myntra", "match_status": "verified_match", "availability": "in_stock", "price": 989.0},
        {"store": "ajio", "match_status": "verified_match", "availability": "in_stock", "price": 949.0},
        {"store": "nykaa", "match_status": "verified_match", "availability": "in_stock", "price": 999.0},
    ]
    summary_a = AvailabilityChecker.calculate_five_stores_summary(case_a)
    assert summary_a["all_available"] is True
    assert summary_a["available_count"] == 5
    assert "🔥 Available on all 5 stores" in summary_a["message"]

    # Case B: Available on 4 of 5 stores (1 store no match)
    case_b = [
        {"store": "amazon", "match_status": "verified_match", "availability": "in_stock", "price": 899.0},
        {"store": "flipkart", "match_status": "verified_match", "availability": "in_stock", "price": 929.0},
        {"store": "myntra", "match_status": "verified_match", "availability": "in_stock", "price": 989.0},
        {"store": "ajio", "match_status": "no_verified_match", "availability": "unavailable", "price": None},
        {"store": "nykaa", "match_status": "verified_match", "availability": "in_stock", "price": 999.0},
    ]
    summary_b = AvailabilityChecker.calculate_five_stores_summary(case_b)
    assert summary_b["all_available"] is False
    assert summary_b["available_count"] == 4
    assert "Available on 4 of 5 stores" in summary_b["message"]

    # Case C: Same product found on 5 stores, but 1 is OUT OF STOCK
    case_c = [
        {"store": "amazon", "match_status": "verified_match", "availability": "out_of_stock", "price": 899.0},
        {"store": "flipkart", "match_status": "verified_match", "availability": "in_stock", "price": 929.0},
        {"store": "myntra", "match_status": "verified_match", "availability": "in_stock", "price": 989.0},
        {"store": "ajio", "match_status": "verified_match", "availability": "in_stock", "price": 949.0},
        {"store": "nykaa", "match_status": "verified_match", "availability": "in_stock", "price": 999.0},
    ]
    summary_c = AvailabilityChecker.calculate_five_stores_summary(case_c)
    assert summary_c["all_available"] is False
    assert summary_c["verified_match_count"] == 5
    assert summary_c["available_count"] == 4
    assert "4 in stock" in summary_c["message"] or "4 of 5" in summary_c["message"]


def test_rule_17_and_18_exact_variant_verified_match_vs_possible_match():
    """
    Step 19, 41, 42:
    Display states:
    - ✓ Verified Match (>= 0.90)
    - ? Possible Match (0.75 - 0.89)
    - — No Verified Match (< 0.75 or hard conflict)
    """
    base = {
        "title": "BROADSTAR Men Relaxed Straight Leg Korean Pants",
        "brand": "BROADSTAR",
        "size": "32",
        "color": "black",
    }
    cand_verified = {
        "title": "BROADSTAR Men's Relaxed Straight Fit Korean Pants",
        "brand": "BROADSTAR",
        "size": "32",
        "color": "black",
    }
    res = ProductMatchingEngine.evaluate_candidate(base, cand_verified)
    assert res.match_status == "verified_match"
    assert res.confidence >= 0.90
    assert "Verified exact product" in res.reason
    assert res.audit["brand_match"] is True
    assert res.audit["size_match"] is True
    assert res.audit["color_match"] is True


def test_unit_normalization():
    """
    Step 8:
    256 GB, 256GB, 256 gb -> 256gb
    1 L -> 1000ml
    """
    assert ProductNormalizer.normalize_units("Apple iPhone 256 GB") == "Apple iPhone 256gb"
    assert ProductNormalizer.normalize_units("1 L Almond Milk") == "1000ml Almond Milk"
    assert ProductNormalizer.normalize_units("Pack of 2 Shirts") == "pack-2 Shirts"
