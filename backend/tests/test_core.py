"""
Unit tests for PriceWatch India backend.
Tests the alert evaluation logic and platform detection.
"""
import pytest
from unittest.mock import MagicMock
from datetime import datetime

from services.platform_fetcher import detect_platform, PlatformEnum
from worker.tasks import evaluate_alert
from db.models import PriceAlert, AlertTypeEnum, AlertStatusEnum, Product, AvailabilityEnum


def make_product(price: float) -> Product:
    p = Product()
    p.current_price = price
    p.platform = PlatformEnum.amazon
    p.availability = AvailabilityEnum.in_stock
    return p


def make_alert(**kwargs) -> PriceAlert:
    a = PriceAlert()
    a.alert_type = kwargs.get("alert_type", AlertTypeEnum.below_price)
    a.target_price = kwargs.get("target_price", None)
    a.minimum_price = kwargs.get("minimum_price", None)
    a.maximum_price = kwargs.get("maximum_price", None)
    a.percentage_drop = kwargs.get("percentage_drop", None)
    a.base_price = kwargs.get("base_price", None)
    a.is_in_range = kwargs.get("is_in_range", False)
    a.alert_status = AlertStatusEnum.active
    return a


# ---- Platform Detection Tests ----

class TestPlatformDetection:
    def test_amazon_in(self):
        assert detect_platform("https://www.amazon.in/dp/B0CXYZ") == PlatformEnum.amazon

    def test_amzn_in(self):
        assert detect_platform("https://amzn.in/d/shortlink") == PlatformEnum.amazon

    def test_flipkart(self):
        assert detect_platform("https://www.flipkart.com/phone/p/itm123") == PlatformEnum.flipkart

    def test_ajio(self):
        assert detect_platform("https://www.ajio.com/product/jeans") == PlatformEnum.ajio

    def test_myntra(self):
        assert detect_platform("https://www.myntra.com/shirts/hm/shirt") == PlatformEnum.myntra

    def test_nykaa(self):
        assert detect_platform("https://www.nykaa.com/foundation") == PlatformEnum.nykaa

    def test_unknown(self):
        assert detect_platform("https://www.meesho.com/product") == PlatformEnum.unknown

    def test_empty(self):
        assert detect_platform("") == PlatformEnum.unknown


# ---- Alert Evaluation Tests ----

class TestAlertEvaluation:
    def test_below_price_triggered(self):
        alert = make_alert(alert_type=AlertTypeEnum.below_price, target_price=50000)
        product = make_product(48000)
        met, desc = evaluate_alert(alert, product)
        assert met is True
        assert "48,000" in desc or "48000" in desc

    def test_below_price_not_triggered(self):
        alert = make_alert(alert_type=AlertTypeEnum.below_price, target_price=50000)
        product = make_product(55000)
        met, desc = evaluate_alert(alert, product)
        assert met is False

    def test_price_range_triggered(self):
        alert = make_alert(
            alert_type=AlertTypeEnum.price_range,
            minimum_price=45000,
            maximum_price=55000,
        )
        product = make_product(50000)
        met, desc = evaluate_alert(alert, product)
        assert met is True

    def test_price_range_below_min(self):
        alert = make_alert(
            alert_type=AlertTypeEnum.price_range,
            minimum_price=45000,
            maximum_price=55000,
        )
        product = make_product(40000)
        met, _ = evaluate_alert(alert, product)
        assert met is False

    def test_price_range_above_max(self):
        alert = make_alert(
            alert_type=AlertTypeEnum.price_range,
            minimum_price=45000,
            maximum_price=55000,
        )
        product = make_product(60000)
        met, _ = evaluate_alert(alert, product)
        assert met is False

    def test_percentage_drop_triggered(self):
        alert = make_alert(
            alert_type=AlertTypeEnum.percentage_drop,
            percentage_drop=20.0,
            base_price=100000,
        )
        product = make_product(75000)  # 25% drop
        met, desc = evaluate_alert(alert, product)
        assert met is True

    def test_percentage_drop_not_triggered(self):
        alert = make_alert(
            alert_type=AlertTypeEnum.percentage_drop,
            percentage_drop=20.0,
            base_price=100000,
        )
        product = make_product(90000)  # Only 10% drop
        met, _ = evaluate_alert(alert, product)
        assert met is False

    def test_no_price_no_trigger(self):
        alert = make_alert(alert_type=AlertTypeEnum.below_price, target_price=50000)
        product = make_product(0)
        product.current_price = None
        met, _ = evaluate_alert(alert, product)
        assert met is False
