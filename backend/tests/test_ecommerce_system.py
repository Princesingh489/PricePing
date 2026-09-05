import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from ecommerce.product_matcher import extract_specs, is_strict_match
from ecommerce.registry import registry
from services.historical_provider import historical_provider, calculate_real_statistics


def test_spec_extraction_and_strict_variant_matching():
    """
    Test Requirement:
    'iPhone 16 128 GB Black MUST NOT be incorrectly matched with iPhone 16 256 GB Black.'
    """
    spec_128 = extract_specs("Apple iPhone 16 (128 GB) - Black")
    spec_256 = extract_specs("Apple iPhone 16 (256 GB) - Black")
    spec_128_same = extract_specs("iPhone 16 128GB Black Smartphone")

    assert spec_128["brand"] == "apple"
    assert spec_128["storage"] == "128gb"
    assert spec_128["color"] == "black"

    assert spec_256["brand"] == "apple"
    assert spec_256["storage"] == "256gb"

    # Strict match check: different storage capacities MUST reject
    match_diff, score_diff, reason_diff = is_strict_match(
        "Apple iPhone 16 (128 GB) - Black",
        "Apple iPhone 16 (256 GB) - Black",
        candidate_brand="apple",
        base_brand="apple"
    )
    assert not match_diff, "Incompatible storage variants must reject match"
    assert "Storage variant mismatch" in reason_diff

    # Same storage capacity MUST match
    match_same, score_same, reason_same = is_strict_match(
        "Apple iPhone 16 (128 GB) - Black",
        "Apple iPhone 16 128GB Black Smartphone",
        candidate_brand="apple",
        base_brand="apple"
    )
    assert match_same, f"Identical variant must match: {reason_same}"


def test_ecommerce_adapters_detection_and_extraction():
    """
    Test adapters for Amazon, Flipkart, Myntra, AJIO, Nykaa.
    """
    amazon_url = "https://www.amazon.in/Apple-iPhone-16-128-GB/dp/B0BDHW4P47?th=1"
    flipkart_url = "https://www.flipkart.com/apple-iphone-16-black-128-gb/p/itme?pid=MOBGTAGP4P&lid=LST"
    myntra_url = "https://www.myntra.com/smartphones/apple/apple-iphone-16-128gb/29182344/buy"
    ajio_url = "https://www.ajio.com/apple-iphone-16-128gb/p/469123456_black"
    nykaa_url = "https://www.nykaa.com/apple-iphone-16/p/10928374?skuId=10928375"

    amazon_adapter = registry.get_adapter_by_store("amazon")
    flipkart_adapter = registry.get_adapter_by_store("flipkart")
    myntra_adapter = registry.get_adapter_by_store("myntra")
    ajio_adapter = registry.get_adapter_by_store("ajio")
    nykaa_adapter = registry.get_adapter_by_store("nykaa")

    assert amazon_adapter.detect_url(amazon_url)
    assert amazon_adapter.extract_product_id(amazon_url) == "B0BDHW4P47"

    assert flipkart_adapter.detect_url(flipkart_url)
    assert flipkart_adapter.extract_product_id(flipkart_url) == "MOBGTAGP4P"

    assert myntra_adapter.detect_url(myntra_url)
    assert myntra_adapter.extract_product_id(myntra_url) == "29182344"

    assert ajio_adapter.detect_url(ajio_url)
    assert ajio_adapter.extract_product_id(ajio_url) == "469123456_black"

    assert nykaa_adapter.detect_url(nykaa_url)
    assert nykaa_adapter.extract_product_id(nykaa_url) == "10928374"


def test_real_statistics_calculation_without_synthetic_data():
    """
    Test genuine math calculations:
    Average, lowest, highest, median, days since lowest.
    Ensures zero fake data is injected.
    """
    class MockProduct:
        id = 1
        current_price = 74999.0
        original_price = 79900.0
        lowest_price = 72999.0
        highest_price = 79900.0

    today = datetime.utcnow()
    d1 = (today - timedelta(days=20)).isoformat()
    d2 = (today - timedelta(days=10)).isoformat()
    d3 = (today - timedelta(days=2)).isoformat()

    observations = [
        {"price": 79900.0, "timestamp": d1, "date": "May 1", "store": "amazon", "source": "priceping_observation"},
        {"price": 72999.0, "timestamp": d2, "date": "May 11", "store": "amazon", "source": "priceping_observation"},
        {"price": 74999.0, "timestamp": d3, "date": "May 19", "store": "amazon", "source": "priceping_observation"},
    ]

    stats = calculate_real_statistics(MockProduct(), observations)

    assert stats["current_price"] == 74999.0
    assert stats["lowest_price"] == 72999.0
    assert stats["highest_price"] == 79900.0
    assert stats["average_price"] == 75966.0
    assert stats["median_price"] == 74999.0
    assert stats["observation_count"] == 3
    assert stats["is_reliable"] is True
    assert stats["lowest_price_date"] == "May 11"
    assert stats["highest_price_date"] == "May 1"
    assert stats["days_since_lowest"] == 10
    assert stats["recommendation"] in ["BUY_NOW", "FAIR_PRICE", "WAIT", "WATCH"]


def test_insufficient_history_handling():
    """
    Test when there are no historical observations:
    Does NOT manufacture a graph, but reports insufficient data gracefully.
    """
    class MockProduct:
        id = 2
        current_price = 4999.0
        original_price = 5999.0
        lowest_price = 4999.0
        highest_price = 5999.0

    stats = calculate_real_statistics(MockProduct(), [])

    assert stats["observation_count"] == 0
    assert stats["is_reliable"] is False
    assert stats["recommendation"] == "INSUFFICIENT_DATA"
    assert "No verified price history is available" in stats["recommendation_reason"]


def test_anti_accessory_and_device_discrimination():
    """
    Test Requirement:
    Phone cases, tempered glass, cables, or covers MUST NEVER match the actual core device,
    even if the title contains all brand and model tokens.
    """
    # 1. iPhone 16 Tempered Glass vs Apple iPhone 16
    res1 = is_strict_match(
        base_title="Apple iPhone 16 (128 GB) - Black",
        candidate_title="Spigen Tempered Glass Screen Protector for Apple iPhone 16 (Black)",
        base_brand="apple",
        candidate_brand="spigen",
    )
    assert not res1.is_match, "Accessory (Screen Protector) must be rejected against core device"
    assert res1.confidence == 0.0
    assert "accessory" in res1.reason.lower()
    assert res1.signals["accessory_match"] is False

    # 2. Silicone Case vs iPhone 16
    res2 = is_strict_match(
        base_title="Apple iPhone 16 (128 GB) - Black",
        candidate_title="Shockproof Liquid Silicone Back Case Cover for iPhone 16 128GB Black",
        base_brand="apple",
    )
    assert not res2.is_match, "Back Case Cover must be rejected against core device"
    assert res2.confidence == 0.0
    assert res2.signals["accessory_match"] is False

    # 3. RAM variant mismatch: 8GB RAM vs 12GB RAM
    res3 = is_strict_match(
        base_title="OnePlus 12 (12GB RAM, 256GB Storage, Silky Black)",
        candidate_title="OnePlus 12 (16GB RAM, 256GB Storage, Silky Black)",
        base_brand="oneplus",
    )
    assert not res3.is_match, "RAM mismatch (12GB vs 16GB) must be rejected"
    assert "RAM variant mismatch" in res3.reason
    assert res3.signals["ram_match"] is False

    # 4. Backward compatible 3-tuple unpacking
    is_match, conf, reason = is_strict_match(
        base_title="Apple iPhone 16 (128 GB) - Black",
        candidate_title="Apple iPhone 16 (128 GB) - Black",
        base_brand="apple",
    )
    assert is_match is True
    assert conf >= 0.85
    assert hasattr(is_strict_match(
        base_title="Apple iPhone 16 (128 GB) - Black",
        candidate_title="Apple iPhone 16 (128 GB) - Black",
        base_brand="apple",
    ), "signals")


def test_multi_price_per_size_variant_extraction():
    """
    Test extraction of per-size variant arrays from Myntra and AJIO HTML payloads.
    Ensures S, M, L, XL have distinct prices and are not collapsed to a single price.
    """
    from bs4 import BeautifulSoup
    from scrapers.myntra.extractors import MyntraExtractor
    from scrapers.ajio.extractors import AjioExtractor

    # 1. Myntra window.__myx script extraction
    myntra_html = """
    <html>
      <head>
        <script>
          window.__myx = {
            "pdpData": {
              "id": 12345,
              "name": "Men Slim Fit Casual Shirt",
              "sizes": [
                {"label": "S", "price": {"discounted": 899, "mrp": 1999}, "available": true, "inventory": 5},
                {"label": "M", "price": {"discounted": 999, "mrp": 1999}, "available": true, "inventory": 10},
                {"label": "L", "price": {"discounted": 1099, "mrp": 1999}, "available": false, "inventory": 0}
              ]
            }
          };
        </script>
      </head>
      <body>
        <div class="pdp-details"></div>
      </body>
    </html>
    """
    soup_m = BeautifulSoup(myntra_html, "lxml")
    m_variants = MyntraExtractor.extract_variants(soup_m, soup_m, default_price=999.0, default_mrp=1999.0)
    assert len(m_variants) == 3
    assert m_variants[0]["size"] == "S" and m_variants[0]["price"] == 899.0 and m_variants[0]["in_stock"] is True
    assert m_variants[1]["size"] == "M" and m_variants[1]["price"] == 999.0 and m_variants[1]["in_stock"] is True
    assert m_variants[2]["size"] == "L" and m_variants[2]["price"] == 1099.0 and m_variants[2]["in_stock"] is False

    # 2. AJIO window.__PRELOADED_STATE__ script extraction
    ajio_html = """
    <html>
      <head>
        <script>
          window.__PRELOADED_STATE__ = {
            "product": {
              "productDetails": {
                "code": "461234",
                "fnlColorVariantData": {
                  "variants": [
                    {"size": "32", "price": {"value": 1299}, "wasPriceData": {"value": 2499}, "inStock": true},
                    {"size": "34", "price": {"value": 1399}, "wasPriceData": {"value": 2499}, "inStock": true},
                    {"size": "36", "price": {"value": 1499}, "wasPriceData": {"value": 2499}, "inStock": false}
                  ]
                }
              }
            }
          };
        </script>
      </head>
      <body></body>
    </html>
    """
    soup_a = BeautifulSoup(ajio_html, "lxml")
    a_variants = AjioExtractor.extract_variants(soup_a, soup_a, default_price=1299.0, default_mrp=2499.0)
    assert len(a_variants) == 3
    assert a_variants[0]["size"] == "32" and a_variants[0]["price"] == 1299.0 and a_variants[0]["in_stock"] is True
    assert a_variants[1]["size"] == "34" and a_variants[1]["price"] == 1399.0 and a_variants[1]["in_stock"] is True
    assert a_variants[2]["size"] == "36" and a_variants[2]["price"] == 1499.0 and a_variants[2]["in_stock"] is False


def test_cross_store_comparison_matrix_structure():
    """
    Test that EcommerceRegistry returns a standardized 5-store comparison matrix
    with observed_at, match diagnostics, and variants.
    """
    import asyncio

    base_product = {
        "store": "amazon",
        "title": "Apple iPhone 16 (128 GB) - Black",
        "brand": "apple",
        "model": "iphone 16",
        "variant": "128gb, black",
        "price": 74999.0,
        "original_price": 79900.0,
        "url": "https://www.amazon.in/dp/B0BDHW4P47",
        "product_id": "B0BDHW4P47",
        "availability": "in_stock",
        "variants": [{"size": "128GB", "price": 74999.0, "mrp": 79900.0, "in_stock": True, "sku": "B0BDHW4P47"}],
    }

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    comparison = loop.run_until_complete(registry.fetch_cross_store_comparison(base_product))
    loop.close()

    assert len(comparison) == 5, f"Expected 5 stores in matrix, got {len(comparison)}"
    stores_present = {c["store"] for c in comparison}
    assert stores_present == {"amazon", "flipkart", "myntra", "ajio", "nykaa"}

    # Origin store checks
    amazon_res = next(c for c in comparison if c["store"] == "amazon")
    assert amazon_res["status"] == "available"
    assert amazon_res["is_verified_match"] is True
    assert amazon_res["price"] == 74999.0
    assert amazon_res["match_confidence"] == 1.0
    assert amazon_res["observed_at"] is not None
    assert len(amazon_res["variants"]) == 1
    assert amazon_res["variants"][0]["size"] == "128GB"

    # All stores must have standardized fields
    for store_offer in comparison:
        assert "store" in store_offer
        assert "status" in store_offer
        assert store_offer["status"] in ("available", "no_match", "unavailable")
        assert "is_verified_match" in store_offer
        assert "match_confidence" in store_offer
        assert "variants" in store_offer
        assert "observed_at" in store_offer


if __name__ == "__main__":
    test_spec_extraction_and_strict_variant_matching()
    test_ecommerce_adapters_detection_and_extraction()
    test_real_statistics_calculation_without_synthetic_data()
    test_insufficient_history_handling()
    test_anti_accessory_and_device_discrimination()
    test_multi_price_per_size_variant_extraction()
    test_cross_store_comparison_matrix_structure()
    print("ALL ECOMMERCE SYSTEM TESTS (INCLUDING STRICT MATCHING & VARIANTS) PASSED SUCCESSFULLY! (7/7)")
