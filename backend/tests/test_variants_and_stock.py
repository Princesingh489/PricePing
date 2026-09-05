"""
Variant & Stock Accuracy Tests
==============================
Tests for:
1. Selected variant resolution (Size, Color, Shade, Style)
2. Scoped buybox stock detection (No false out-of-stock)
3. Mathematical discount validation
"""
import pytest
from unittest.mock import patch, AsyncMock
from scrapers.flipkart.scraper import FlipkartScraper
from scrapers.amazon.scraper import AmazonScraper
from scrapers.myntra.scraper import MyntraScraper
from scrapers.ajio.scraper import AjioScraper
from scrapers.nykaa.scraper import NykaaScraper
from scrapers.cache import ScraperCache
from db.models import AvailabilityEnum


@pytest.fixture(autouse=True)
def clear_cache():
    ScraperCache.clear_all()


@pytest.mark.asyncio
async def test_flipkart_selected_variant_and_stock():
    """
    Simulates the exact user problem:
    Flipkart product with active size 7, color DKBLUE, price 930, MRP 1999 (53% off),
    with Add to Cart active (must be in_stock, not out_of_stock).
    """
    html = """
    <html>
    <body>
        <div class="DOjaWF YJG4Cf">
            <span class="VU-ZEz">ADIDAS Running Shoes For Men</span>
            <div class="Nx9bqj CxhGGd">₹930</div>
            <div class="yRaY8j A68aAq">₹1,999</div>
            <div class="UkUFwK"><span>53% off</span></div>
            <div class="_1fJS1d _20WOHl">7</div>
            <a class="_2dq9f_ active" alt="DKBLUE/FTWWHT/DKBLUE"></a>
            <img class="DByuf4" src="https://rukminim1.flixcart.com/image/832/832/shoes.jpg" />
            <button class="_2KpZ6l _2U9uOA _3v1-ww">ADD TO CART</button>
            <button class="_2KpZ6l _2U9uOA _3AWRsL">BUY NOW</button>
        </div>
    </body>
    </html>
    """
    scraper = FlipkartScraper()
    with patch("scrapers.playwright_manager.PlaywrightManager.fetch_html", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = (html, "playwright")
        res = await scraper.extract_product("https://www.flipkart.com/adidas-shoes/p/itm12345?pid=SHOE123&lid=LST123&size=7&color=DKBLUE")

        assert res.success is True
        assert res.current_price == 930.0
        assert res.original_price == 1999.0
        assert res.discount_percentage == 53.0
        assert res.availability == AvailabilityEnum.in_stock
        assert res.variant is not None
        assert res.variant.get("size") == "7"
        assert res.variant.get("color") == "DKBLUE/FTWWHT/DKBLUE"
        assert res.confidence_score >= 85


@pytest.mark.asyncio
async def test_flipkart_out_of_stock_variant():
    """
    Simulates Flipkart product where the active variant is out of stock (Notify Me).
    """
    html = """
    <html>
    <body>
        <div class="DOjaWF YJG4Cf">
            <span class="VU-ZEz">Puma Running Shoes</span>
            <div class="Nx9bqj CxhGGd">₹1,499</div>
            <div class="_1fJS1d _20WOHl">9</div>
            <button class="_2KpZ6l _2U9uOA _31hAvH">NOTIFY ME</button>
        </div>
    </body>
    </html>
    """
    scraper = FlipkartScraper()
    with patch("scrapers.playwright_manager.PlaywrightManager.fetch_html", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = (html, "playwright")
        res = await scraper.extract_product("https://www.flipkart.com/puma-shoes/p/itm987?pid=PUMA987&size=9")

        assert res.success is True
        assert res.current_price == 1499.0
        assert res.availability == AvailabilityEnum.out_of_stock
        assert res.variant.get("size") == "9"


@pytest.mark.asyncio
async def test_amazon_selected_variant_twister():
    """
    Simulates Amazon product with selected color and size in #inline-twister-row.
    """
    html = """
    <html>
    <body>
        <div id="ppd">
            <h1 id="productTitle">boAt Airdopes 141 Bluetooth Earbuds</h1>
            <div id="inline-twister-row-color_name"><span class="selection">Bold Black</span></div>
            <div id="inline-twister-row-size_name"><span class="selection">Standard</span></div>
            <div id="corePriceDisplay_desktop_feature_div">
                <span class="a-price a-price-whole">1,299<span class="a-price-decimal">.</span></span>
            </div>
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
        res = await scraper.extract_product("https://www.amazon.in/dp/B09N3ZNHTY")

        assert res.success is True
        assert res.current_price == 1299.0
        assert res.availability == AvailabilityEnum.in_stock
        assert res.variant is not None
        assert res.variant.get("color") == "Bold Black"
        assert res.variant.get("size") == "Standard"


@pytest.mark.asyncio
async def test_myntra_selected_size_and_bag():
    """
    Simulates Myntra product with selected size button and active bag button.
    """
    html = """
    <html>
    <body>
        <div class="pdp-details">
            <h1 class="pdp-title">Roadster</h1>
            <h1 class="pdp-name">Solid Cotton T-Shirt</h1>
            <span class="pdp-price">₹499</span>
            <span class="pdp-mrp">₹999</span>
            <button class="size-buttons-size-button size-buttons-size-button-selected">M</button>
            <div class="pdp-add-to-bag">ADD TO BAG</div>
        </div>
    </body>
    </html>
    """
    scraper = MyntraScraper()
    with patch("scrapers.playwright_manager.PlaywrightManager.fetch_html", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = (html, "playwright")
        res = await scraper.extract_product("https://www.myntra.com/tshirts/roadster/12345/buy")

        assert res.success is True
        assert res.current_price == 499.0
        assert res.original_price == 999.0
        assert res.discount_percentage == 50.0
        assert res.availability == AvailabilityEnum.in_stock
        assert res.variant.get("size") == "M"


@pytest.mark.asyncio
async def test_ajio_selected_color_and_size():
    """
    Simulates AJIO product with selected color from URL and active size swatch.
    """
    html = """
    <html>
    <body>
        <div class="prod-content">
            <h2 class="brand-name">GAP</h2>
            <h1 class="prod-name">Men Slim Fit Shirt</h1>
            <span class="prod-sp">₹1,299</span>
            <span class="prod-cp">₹2,499</span>
            <div class="size-variant-item selected">L</div>
            <div class="btn-gold">ADD TO BAG</div>
        </div>
    </body>
    </html>
    """
    scraper = AjioScraper()
    with patch("scrapers.playwright_manager.PlaywrightManager.fetch_html", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = (html, "playwright")
        res = await scraper.extract_product("https://www.ajio.com/gap-shirt/p/460788224_navy")

        assert res.success is True
        assert res.current_price == 1299.0
        assert res.original_price == 2499.0
        assert res.availability == AvailabilityEnum.in_stock
        assert res.variant.get("color") == "Navy"
        assert res.variant.get("size") == "L"


@pytest.mark.asyncio
async def test_nykaa_selected_shade():
    """
    Simulates Nykaa lipstick with selected shade.
    """
    html = """
    <html>
    <body>
        <div class="product-details">
            <h1 class="css-1gc4x7i">M.A.C Retro Matte Lipstick</h1>
            <span class="css-1jczs19">₹1,950</span>
            <div class="shade-selector selected">Ruby Woo</div>
            <button class="css-1r0r6u9">Add to Bag</button>
        </div>
    </body>
    </html>
    """
    scraper = NykaaScraper()
    with patch("scrapers.playwright_manager.PlaywrightManager.fetch_html", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = (html, "playwright")
        res = await scraper.extract_product("https://www.nykaa.com/mac-retro-matte-lipstick/p/12345")

        assert res.success is True
        assert res.current_price == 1950.0
        assert res.availability == AvailabilityEnum.in_stock
        assert res.variant.get("shade") == "Ruby Woo"
