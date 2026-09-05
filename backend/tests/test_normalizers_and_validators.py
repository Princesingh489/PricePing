import pytest
from db.models import PlatformEnum, AvailabilityEnum
from scrapers.normalizers import PriceNormalizer, NumberNormalizer
from scrapers.validators import PriceValidator, ProductValidator, ConfidenceValidator
from scrapers.extractors import PriceExtractor, PriceCandidate, DomExtractor, ImageExtractor


def test_price_normalizer_clean_prices():
    assert PriceNormalizer.clean_price("₹1,49,900.00") == 149900.0
    assert PriceNormalizer.clean_price("Rs. 1,299") == 1299.0
    assert PriceNormalizer.clean_price("INR 499.50") == 499.50
    assert PriceNormalizer.clean_price("899") == 899.0
    assert PriceNormalizer.clean_price(1999) == 1999.0
    assert PriceNormalizer.clean_price(0) is None
    assert PriceNormalizer.clean_price("-50") is None


def test_price_normalizer_rejects_non_prices():
    # EMI
    assert PriceNormalizer.clean_price("EMI from ₹120/mo") is None
    assert PriceNormalizer.clean_price("₹40/month") is None
    assert PriceNormalizer.clean_price("No Cost EMI Available") is None
    # Coupons & Offers
    assert PriceNormalizer.clean_price("Save ₹50 with coupon") is None
    assert PriceNormalizer.clean_price("Coupon discount: ₹30") is None
    assert PriceNormalizer.clean_price("10% off on exchange") is None
    assert PriceNormalizer.clean_price("Exchange value up to ₹1,000") is None
    assert PriceNormalizer.clean_price("Delivery fee: ₹40") is None


def test_number_normalizer_ratings():
    assert NumberNormalizer.parse_rating("4.2 ★") == 4.2
    assert NumberNormalizer.parse_rating("4.5 out of 5 stars") == 4.5
    assert NumberNormalizer.parse_rating("3.9 / 5") == 3.9
    assert NumberNormalizer.parse_rating("5.0") == 5.0
    assert NumberNormalizer.parse_rating("0.0") == 0.0
    assert NumberNormalizer.parse_rating(4.8) == 4.8
    assert NumberNormalizer.parse_rating("6.5") is None  # Out of range
    assert NumberNormalizer.parse_rating("-1.0") is None


def test_number_normalizer_counts():
    assert NumberNormalizer.parse_count("1,48,271 Ratings") == 148271
    assert NumberNormalizer.parse_count("1.2 lakh") == 120000
    assert NumberNormalizer.parse_count("2.5K") == 2500
    assert NumberNormalizer.parse_count("10K") == 10000
    assert NumberNormalizer.parse_count("1.5M") == 1500000
    assert NumberNormalizer.parse_count("59 Reviews") == 59
    assert NumberNormalizer.parse_count(1622) == 1622


def test_price_validator_mathematical_discount():
    # Regular 60% discount
    curr, orig, disc = PriceValidator.validate_prices(200.0, 498.0)
    assert curr == 200.0
    assert orig == 498.0
    assert disc == 60.0  # round(((498-200)/498)*100) = round(59.839) = 60.0

    # MRP equal to price (no discount)
    curr, orig, disc = PriceValidator.validate_prices(500.0, 500.0)
    assert curr == 500.0
    assert orig == 500.0
    assert disc is None

    # MRP less than current price (invalid MRP rejected)
    curr, orig, disc = PriceValidator.validate_prices(600.0, 400.0)
    assert curr == 600.0
    assert orig is None
    assert disc is None


def test_price_validator_spike_protection():
    # 60% price drop -> suspicious
    assert PriceValidator.is_price_spike_suspicious(1000.0, 400.0) is True
    # 10% price drop -> normal
    assert PriceValidator.is_price_spike_suspicious(1000.0, 900.0) is False
    # 400% price spike -> suspicious
    assert PriceValidator.is_price_spike_suspicious(100.0, 500.0) is True


def test_confidence_validator_scoring():
    cand1 = PriceCandidate(value=200.0, source="dom", label="current_price", confidence_weight=45)
    candidates = [cand1]

    # High confidence test
    score = ConfidenceValidator.calculate_confidence(
        selected_price=200.0,
        candidates=candidates,
        has_main_container=True,
        has_title=True,
        has_image=True,
        json_ld_price=200.0,
    )
    assert score >= 85
    assert ConfidenceValidator.is_acceptable(score) is True
    assert ConfidenceValidator.should_fail_closed(score) is False

    # Low confidence test (coupon collision penalty)
    cand_coupon = PriceCandidate(value=30.0, source="coupon", label="coupon_discount", confidence_weight=-80)
    score_low = ConfidenceValidator.calculate_confidence(
        selected_price=30.0,
        candidates=[cand_coupon],
        has_main_container=False,
        has_title=True,
        has_image=False,
        json_ld_price=500.0,
    )
    assert score_low < 70
    assert ConfidenceValidator.should_fail_closed(score_low) is True


def test_image_extractor_flipkart_upscaling():
    thumb = "https://rukminim2.flixcart.com/image/128/128/xif0q/speaker/blue_mivi.jpeg?q=70"
    hires = ImageExtractor.normalize_flipkart_image(thumb)
    assert "/image/832/832/" in hires
    assert "q=90" in hires


def test_image_extractor_placeholder_rejection():
    assert ImageExtractor.sanitize_image_url("https://example.com/spacer.gif") is None
    assert ImageExtractor.sanitize_image_url("https://example.com/logo.png") is None
    assert ImageExtractor.sanitize_image_url("data:image/svg+xml;base64,...") is None
    assert ImageExtractor.sanitize_image_url("https://example.com/product_main.jpg") == "https://example.com/product_main.jpg"
