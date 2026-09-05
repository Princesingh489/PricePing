"""
Price Accuracy, Anti-False Filters & Amount Saved Tests
=======================================================
Verifies:
1. Exact mathematical discount calculation: round(((MRP - Price) / MRP) * 100)
2. Saved amount calculation: round(MRP - Price, 2)
3. Total rejection of coupons, EMI, bank offers, 'Buy at ₹X', exchange discounts
4. Rejection of MRP <= Price
5. Multi-platform extraction of saved_amount
"""
import pytest
from unittest.mock import patch, AsyncMock
from scrapers.shared.normalizers import SharedNormalizer
from scrapers.shared.confidence import ConfidenceEngine
from scrapers.amazon.scraper import AmazonScraper
from scrapers.flipkart.scraper import FlipkartScraper
from scrapers.myntra.scraper import MyntraScraper
from scrapers.ajio.scraper import AjioScraper
from scrapers.nykaa.scraper import NykaaScraper
from scrapers.cache import ScraperCache


@pytest.fixture(autouse=True)
def clear_cache():
    ScraperCache.clear_all()


def test_mathematical_discount_and_saved_amount():
    """
    Current Price = ₹289, Original MRP = ₹499
    Expected: Discount = 42%, Saved Amount = ₹210
    """
    cur, orig, disc, saved = ConfidenceEngine.validate_and_calculate_discount(289.0, 499.0)
    assert cur == 289.0
    assert orig == 499.0
    assert disc == 42.0
    assert saved == 210.0


def test_anti_false_price_rejection_filters():
    """
    Ensure all false promotional price strings are completely rejected.
    """
    rejected_strings = [
        "₹40/month",
        "₹120/mo",
        "EMI starts at ₹150",
        "No cost EMI available",
        "Save ₹50 with coupon",
        "Apply ₹100 coupon",
        "Coupon discount ₹30",
        "Buy at ₹249 with HDFC card",
        "Buy for ₹199",
        "Effective price ₹180",
        "Bank offer ₹50 off",
        "Instant discount ₹75",
        "Credit card offer ₹100 off",
        "Debit card offer ₹50 off",
        "₹500 off on exchange",
        "Exchange value up to ₹2,000",
        "With exchange: ₹15,000",
        "Delivery fee ₹40",
        "Special price get extra ₹100 off",
    ]
    for s in rejected_strings:
        val = SharedNormalizer.clean_price(s)
        assert val is None, f"Expected '{s}' to be rejected, but got {val}"


def test_mrp_less_than_or_equal_to_price_rejection():
    """
    If MRP <= Current Price, MRP must be rejected, and discount/savings must be None.
    """
    # Equal MRP and Price
    cur, orig, disc, saved = ConfidenceEngine.validate_and_calculate_discount(500.0, 500.0)
    assert cur == 500.0
    assert orig is None
    assert disc is None
    assert saved is None

    # MRP lower than price
    cur, orig, disc, saved = ConfidenceEngine.validate_and_calculate_discount(500.0, 400.0)
    assert cur == 500.0
    assert orig is None
    assert disc is None
    assert saved is None


@pytest.mark.asyncio
async def test_amazon_price_and_savings_extraction():
    """
    Test Amazon product extracting selling price ₹289, MRP ₹499, 42% OFF, Save ₹210.
    """
    html = """
    <html>
    <body>
        <div id="ppd">
            <h1 id="productTitle">boAt Bassheads 100 Wired Earphones</h1>
            <div id="corePriceDisplay_desktop_feature_div">
                <span class="a-price a-price-whole">289<span class="a-price-decimal">.</span></span>
            </div>
            <span class="a-price a-text-price"><span class="a-offscreen">₹499</span></span>
            <div id="desktop_buybox">
                <input id="add-to-cart-button" type="submit" value="Add to Cart" />
            </div>
        </div>
    </body>
    </html>
    """
    scraper = AmazonScraper()
    with patch("scrapers.playwright_manager.PlaywrightManager.fetch_html", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = (html, "playwright")
        res = await scraper.extract_product("https://www.amazon.in/dp/B071Z8M4KX")

        assert res.success is True
        assert res.current_price == 289.0
        assert res.original_price == 499.0
        assert res.discount_percentage == 42.0
        assert res.saved_amount == 210.0
        assert res["saved_amount"] == 210.0
        assert res["you_save"] == 210.0


@pytest.mark.asyncio
async def test_flipkart_price_and_savings_extraction():
    """
    Test Flipkart product extracting selling price ₹930, MRP ₹1,999, 53% OFF, Save ₹1069.
    """
    html = """
    <html>
    <body>
        <div class="DOjaWF YJG4Cf">
            <span class="VU-ZEz">ADIDAS Running Shoes For Men</span>
            <div class="Nx9bqj CxhGGd">₹930</div>
            <div class="yRaY8j A68aAq">₹1,999</div>
            <div class="_1fJS1d _20WOHl">7</div>
            <button class="_2KpZ6l _2U9uOA _3v1-ww">ADD TO CART</button>
        </div>
    </body>
    </html>
    """
    scraper = FlipkartScraper()
    with patch("scrapers.playwright_manager.PlaywrightManager.fetch_html", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = (html, "playwright")
        res = await scraper.extract_product("https://www.flipkart.com/adidas-shoes/p/itm123?pid=SHOE123")

        assert res.success is True
        assert res.current_price == 930.0
        assert res.original_price == 1999.0
        assert res.discount_percentage == 53.0
        assert res.saved_amount == 1069.0


@pytest.mark.asyncio
async def test_flipkart_motorola_washing_machine_title_and_mrp_savings():
    """
    Test Flipkart appliance (Motorola washing machine) with Price in India title and strikethrough MRP/discount.
    """
    html = """
    <html>
    <head>
        <title>MOTOROLA 9 kg Fully Automatic Front Load Washing Machine with In-built Heater Blue Price in India - Buy MOTOROLA 9 kg Fully Automatic Front Load Washing Machine with In-built Heater Blue online at Flipkart.com</title>
    </head>
    <body>
        <div class="cPHDOP col-12-12">
            <div class="_25b18c">
                <div class="Nx9bqj CxhGGd">₹25,990</div>
                <div class="yRaY8j">₹38,990</div>
                <div class="UkUFwK"><span>33% off</span></div>
            </div>
            <button class="_2KpZ6l _2U9uOA _3v1-ww">Buy Now</button>
        </div>
    </body>
    </html>
    """
    scraper = FlipkartScraper()
    with patch("scrapers.playwright_manager.PlaywrightManager.fetch_html", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = (html, "playwright")
        res = await scraper.extract_product("https://www.flipkart.com/motorola-9-kg-washing-machine/p/itm123")

        assert res.success is True
        assert "Price in India" not in res.title
        assert res.title == "MOTOROLA 9 kg Fully Automatic Front Load Washing Machine with In-built Heater Blue"
        assert res.current_price == 25990.0
        assert res.original_price == 38990.0
        assert res.discount_percentage == 33.0
        assert res.saved_amount == 13000.0


def test_derive_mrp_when_discount_badge_present():
    """
    If MRP is missing from HTML but discount badge (e.g. 33% off) is present,
    MRP and saved_amount are mathematically derived.
    """
    cur, orig, disc, saved = ConfidenceEngine.validate_and_calculate_discount(25990.0, None, extracted_discount=33.0)
    assert cur == 25990.0
    assert orig == 38791.0
    assert disc == 33.0
    assert saved == 12801.0

