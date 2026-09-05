import pytest
from unittest.mock import patch, AsyncMock
from bs4 import BeautifulSoup
from db.models import PlatformEnum, AvailabilityEnum
from scrapers import (
    detect_store_platform,
    get_scraper_for_url,
    AmazonScraper,
    FlipkartScraper,
    MyntraScraper,
    AjioScraper,
    NykaaScraper,
    ConfidenceEngine,
    route_and_scrape,
    scrape_amazon,
    scrape_flipkart,
    scrape_myntra,
    scrape_nykaa,
    scrape_ajio,
)


def test_detect_store_platform():
    assert detect_store_platform("https://www.amazon.in/dp/B0C5X2MGX3") == PlatformEnum.amazon
    assert detect_store_platform("https://amzn.in/d/abc1234") == PlatformEnum.amazon
    assert detect_store_platform("https://www.flipkart.com/item/p/itm123456789") == PlatformEnum.flipkart
    assert detect_store_platform("https://www.myntra.com/tshirts/brand/12345678/buy") == PlatformEnum.myntra
    assert detect_store_platform("https://www.ajio.com/brand-product/p/460788224_black") == PlatformEnum.ajio
    assert detect_store_platform("https://www.nykaa.com/product/p/1234567") == PlatformEnum.nykaa
    assert detect_store_platform("https://www.unknownstore.com/item") == PlatformEnum.unknown


def test_amazon_product_id_extraction():
    scraper = AmazonScraper()
    assert scraper.extract_product_id("https://www.amazon.in/Noise-Smartwatch/dp/B0C5X2MGX3/ref=sr_1_1") == "B0C5X2MGX3"
    assert scraper.extract_product_id("https://www.amazon.in/gp/product/B09G9BL5CP") == "B09G9BL5CP"
    assert scraper.extract_product_id("https://www.amazon.in/d/B0FHHGZFY7?th=1") == "B0FHHGZFY7"


def test_flipkart_product_id_extraction():
    scraper = FlipkartScraper()
    assert scraper.extract_product_id("https://www.flipkart.com/product/p/itm12345?pid=MOBGTAGFWBAPXGHA") == "MOBGTAGFWBAPXGHA"
    assert scraper.extract_product_id("https://www.flipkart.com/item/p/itm123456789") == "itm123456789"


def test_myntra_product_id_extraction():
    scraper = MyntraScraper()
    assert scraper.extract_product_id("https://www.myntra.com/tshirts/roadster/12345678/buy") == "12345678"
    assert scraper.extract_product_id("https://www.myntra.com/jeans/levis/9876543") == "9876543"


def test_ajio_product_id_extraction():
    scraper = AjioScraper()
    assert scraper.extract_product_id("https://www.ajio.com/men-shirt/p/460788224_black") == "460788224_black"


def test_nykaa_product_id_extraction():
    scraper = NykaaScraper()
    assert scraper.extract_product_id("https://www.nykaa.com/maybelline-fit-me/p/123456") == "123456"
    assert scraper.extract_product_id("https://www.nykaa.com/product?productId=654321") == "654321"


def test_price_sanitization_and_rejection():
    scraper = AmazonScraper()
    # Valid prices with Indian currency formatting
    assert scraper.parse_price("₹ 1,49,900.00") == 149900.0
    assert scraper.parse_price("₹1,299") == 1299.0
    assert scraper.parse_price("15,999.50") == 15999.50

    # Rejected prices (EMI, coupon, cashback, per month)
    assert scraper.parse_price("₹1,299 / month") is None
    assert scraper.parse_price("EMI from ₹450/mo") is None
    assert scraper.parse_price("Save ₹500 with coupon") is None
    assert scraper.parse_price("₹1,000 off on exchange") is None
    assert scraper.parse_price("No Cost EMI available") is None


def test_title_cleaning():
    scraper = AmazonScraper()
    raw = "Noise ColorFit Diamond Smartwatch : Buy Online at Best Price on Amazon.in"
    assert scraper.clean_title(raw) == "Noise ColorFit Diamond Smartwatch"

    raw_fk = "boAt Rockerz 550 Bluetooth Headphones - Flipkart.com"
    assert scraper.clean_title(raw_fk) == "boAt Rockerz 550 Bluetooth Headphones"


def test_flipkart_image_normalization():
    scraper = FlipkartScraper()
    thumb = "https://rukminim2.flixcart.com/image/128/128/xif0q/smartwatch/y/g/z/-original-imagh2k8hvyb5fzg.jpeg?q=70"
    hires = scraper.normalize_flipkart_image(thumb)
    assert "/image/832/832/" in hires


def test_confidence_engine_evaluation():
    # Test High Confidence Verified Product
    score, status, warnings = ConfidenceEngine.evaluate(
        store=PlatformEnum.amazon,
        product_id="B0C5X2MGX3",
        selected_title="Noise ColorFit Diamond Smartwatch",
        title_source="main_product_heading",
        candidate_titles=[
            {"source": "main_product_heading", "value": "Noise ColorFit Diamond Smartwatch"},
            {"source": "json_ld_name", "value": "Noise ColorFit Diamond Smartwatch"}
        ],
        selected_price=1999.0,
        price_source="main_container_corePrice_feature_div",
        candidate_prices=[
            {"source": "main_container_corePrice_feature_div", "value": 1999.0},
            {"source": "json_ld_offer", "value": 1999.0}
        ],
        selected_image="https://m.media-amazon.com/images/I/71abc.jpg",
        image_source="main_image_dynamic_hires",
        candidate_images=[{"source": "main_image", "value": "https://m.media-amazon.com/images/I/71abc.jpg"}],
        availability=AvailabilityEnum.in_stock,
        original_price=5999.0
    )

    assert score >= 70
    assert status == "verified"
    assert len(warnings) == 0

    # Test Low Confidence Missing Price & Product ID
    score_low, status_low, warnings_low = ConfidenceEngine.evaluate(
        store=PlatformEnum.amazon,
        product_id=None,
        selected_title=None,
        title_source=None,
        candidate_titles=[],
        selected_price=None,
        price_source=None,
        candidate_prices=[],
        selected_image=None,
        image_source=None,
        candidate_images=[],
        availability=AvailabilityEnum.unknown
    )

    assert score_low < 70
    assert status_low == "extraction_failed"
    assert len(warnings_low) > 0


@pytest.mark.asyncio
async def test_amazon_scraper_html_parsing():
    mock_amazon_html = """
    <html>
    <head>
        <title>Noise ColorFit Diamond Smartwatch : Buy Online at Best Price on Amazon.in</title>
        <script type="application/ld+json">
        {
            "@type": "Product",
            "name": "Noise ColorFit Diamond Smartwatch",
            "image": "https://m.media-amazon.com/images/I/71jsonld.jpg",
            "offers": {"price": "1999.00", "priceCurrency": "INR"}
        }
        </script>
    </head>
    <body>
        <div id="dp-container">
            <div id="centerCol">
                <h1 id="productTitle">Noise ColorFit Diamond Smartwatch (Gold)</h1>
                <div id="corePrice_feature_div">
                    <span class="a-price a-text-price"><span class="a-offscreen">₹5,999.00</span></span>
                    <span class="a-price"><span class="a-offscreen">₹1,999.00</span></span>
                </div>
                <div id="availability">
                    <span class="a-color-success">In stock</span>
                </div>
            </div>
            <div id="leftCol">
                <img id="landingImage" data-old-hires="https://m.media-amazon.com/images/I/71hires.jpg" src="https://m.media-amazon.com/images/I/71thumb.jpg" />
            </div>
        </div>
    </body>
    </html>
    """

    scraper = AmazonScraper()
    with patch("scrapers.playwright_manager.PlaywrightManager.fetch_html", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = (mock_amazon_html, "playwright")
        result = await scraper.extract_product("https://www.amazon.in/dp/B0C5X2MGX3")

        assert result.success is True
        assert result.store_product_id == "B0C5X2MGX3"
        assert "Noise ColorFit Diamond Smartwatch" in result.title
        assert result.current_price == 1999.0
        assert result.original_price == 5999.0
        assert result.image_url == "https://m.media-amazon.com/images/I/71hires.jpg"
        assert result.confidence_score >= 70
        assert result.status == "verified"


@pytest.mark.asyncio
async def test_flipkart_scraper_html_parsing():
    mock_flipkart_html = """
    <html>
    <head>
        <title>boAt Rockerz 550 Bluetooth Headphones - Flipkart.com</title>
    </head>
    <body>
        <div class="_1YokD2 _3Mn1Gg">
            <span class="VU-ZEz">boAt Rockerz 550 Bluetooth Wireless Headphone</span>
            <div class="Nx9bqj CxhGGd">₹1,499</div>
            <div class="yRaY8j">₹4,999</div>
            <img class="_396cs4 _2amPTt" src="https://rukminim2.flixcart.com/image/128/128/headphone/boat.jpeg" />
        </div>
    </body>
    </html>
    """

    scraper = FlipkartScraper()
    with patch("scrapers.playwright_manager.PlaywrightManager.fetch_html", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = (mock_flipkart_html, "playwright")
        result = await scraper.extract_product("https://www.flipkart.com/item/p/itm12345?pid=BOATGTAGFWBAPXGH")

        assert result.success is True
        assert result.store_product_id == "BOATGTAGFWBAPXGH"
        assert "boAt Rockerz 550" in result.title
        assert result.current_price == 1499.0
        assert result.original_price == 4999.0
        assert result.discount_percentage == 70.0
        assert "/image/832/832/" in result.image_url
        assert result.status == "verified"


@pytest.mark.asyncio
async def test_flipkart_mivi_speaker_parsing():
    mock_mivi_html = """
    <html>
    <head>
        <title>Mivi Play 12HRS Playback, Bass Boosted, TWS Feature, IPX4 5 W Portable Bluetooth Speaker - Mivi: Flipkart.com</title>
    </head>
    <body>
        <div class="DOjaWF">
            <h1 class="_6EBuvT"><span class="VU-ZEz">Mivi Play 12HRS Playback, Bass Boosted, TWS Feature, IPX4 5 W Portable Bluetooth Speaker</span></h1>
            <div class="hl05eU">
                <div class="Nx9bqj CxhGGd">₹899</div>
                <div class="yRaY8j">₹1,999</div>
                <div class="UkUFwK"><span>55% off</span></div>
            </div>
            <div class="q61Yvd">
                <img class="DByuf4" src="https://rukminim2.flixcart.com/image/128/128/xif0q/speaker/blue/mivi-play.jpeg?q=70" alt="Mivi Play" />
            </div>
        </div>
    </body>
    </html>
    """

    scraper = FlipkartScraper()
    with patch("scrapers.playwright_manager.PlaywrightManager.fetch_html", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = (mock_mivi_html, "playwright")
        result = await scraper.extract_product("https://www.flipkart.com/mivi-play-12hrs/p/itmdb2?pid=ACCG6TG4NZHGYWGM")

        assert result.success is True
        assert result.store_product_id == "ACCG6TG4NZHGYWGM"
        assert "Mivi Play" in result.title
        assert result.current_price == 899.0
        assert result.original_price == 1999.0
        assert result.discount_percentage == 55.0
        assert "/image/832/832/" in result.image_url
        assert result.status == "verified"


def test_flipkart_srcset_extraction():
    scraper = FlipkartScraper()
    srcset = "https://rukminim2.flixcart.com/image/128/128/speaker.jpg 128w, https://rukminim2.flixcart.com/image/832/832/speaker.jpg 832w, https://rukminim2.flixcart.com/image/312/312/speaker.jpg 312w"
    best = scraper.extract_largest_from_srcset(srcset)
    assert "/image/832/832/" in best


@pytest.mark.asyncio
async def test_myntra_scraper_html_parsing():
    mock_myntra_html = """
    <html>
    <head>
        <title>Buy Roadster Men Navy Solid Round Neck T Shirt - Tshirts for Men - Myntra</title>
    </head>
    <body>
        <div class="pdp-details">
            <h1 class="pdp-title">Roadster</h1>
            <h1 class="pdp-name">Men Navy Solid Round Neck T-shirt</h1>
            <span class="pdp-price"><strong>₹399</strong></span>
            <span class="pdp-mrp">₹899</span>
        </div>
        <div class="image-grid-container">
            <img class="image-grid-image" src="https://assets.myntassets.com/h_1440,q_90,w_1080/v1/assets/images/12345/roadster.jpg" />
        </div>
    </body>
    </html>
    """

    scraper = MyntraScraper()
    with patch("scrapers.playwright_manager.PlaywrightManager.fetch_html", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = (mock_myntra_html, "playwright")
        result = await scraper.extract_product("https://www.myntra.com/tshirts/roadster/12345678/buy")

        assert result.success is True
        assert result.store_product_id == "12345678"
        assert "Roadster" in result.title
        assert "T-shirt" in result.title
        assert result.current_price == 399.0
        assert result.original_price == 899.0
        assert "myntassets.com" in result.image_url
        assert result.status == "verified"


@pytest.mark.asyncio
async def test_nykaa_scraper_html_parsing():
    mock_nykaa_html = """
    <html>
    <head>
        <title>Maybelline New York Fit Me Matte+Poreless Liquid Foundation - Nykaa</title>
    </head>
    <body>
        <div class="product-details">
            <h1 class="css-1gc4x7i">Maybelline New York Fit Me Matte+Poreless Liquid Foundation</h1>
            <span class="css-1jczs19">₹549</span>
            <span class="css-u05rr">₹699</span>
            <div class="css-1f6y8y8">
                <img src="https://images-static.nykaa.com/media/catalog/product/m/a/maybelline_fitme.jpg" />
            </div>
        </div>
    </body>
    </html>
    """

    scraper = NykaaScraper()
    with patch("scrapers.playwright_manager.PlaywrightManager.fetch_html", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = (mock_nykaa_html, "playwright")
        result = await scraper.extract_product("https://www.nykaa.com/maybelline-fit-me/p/123456")

        assert result.success is True
        assert result.store_product_id == "123456"
        assert "Maybelline" in result.title
        assert result.current_price == 549.0
        assert result.original_price == 699.0
        assert "nykaa.com" in result.image_url
        assert result.status == "verified"


@pytest.mark.asyncio
async def test_ajio_scraper_html_parsing():
    mock_ajio_html = """
    <html>
    <head>
        <title>Buy GAP Men Slim Fit Shirt - AJIO</title>
    </head>
    <body>
        <div class="prod-content">
            <h2 class="brand-name">GAP</h2>
            <h1 class="prod-name">Men Slim Fit Oxford Shirt</h1>
            <span class="prod-sp">₹1,299</span>
            <span class="prod-cp">₹2,499</span>
            <div class="img-holder">
                <img src="https://assets.ajio.com/medias/sys_master/root/ajio/gap_shirt.jpg" />
            </div>
        </div>
    </body>
    </html>
    """

    scraper = AjioScraper()
    with patch("scrapers.playwright_manager.PlaywrightManager.fetch_html", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = (mock_ajio_html, "playwright")
        result = await scraper.extract_product("https://www.ajio.com/gap-shirt/p/460788224_black")

        assert result.success is True
        assert result.store_product_id == "460788224_black"
        assert "GAP" in result.title
        assert result.current_price == 1299.0
        assert result.original_price == 2499.0
        assert "ajio.com" in result.image_url
        assert result.status == "verified"


@pytest.mark.asyncio
async def test_router_standardized_response():
    mock_html = """
    <html>
    <body>
        <div class="Nx9bqj">₹999</div>
        <div class="yRaY8j">₹1,999</div>
        <span class="VU-ZEz">Sample Product</span>
        <div class="XQDdHH">4.2 ★</div>
        <span class="WNMewY"><span>1,48,271 Ratings & 12,450 Reviews</span></span>
        <img class="_396cs4" src="https://rukminim2.flixcart.com/image/128/128/item.jpg"/>
    </body>
    </html>
    """
    with patch("scrapers.playwright_manager.PlaywrightManager.fetch_html", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = (mock_html, "playwright")
        res = await route_and_scrape("https://www.flipkart.com/item/p/itm12345?pid=SAMPLEPID123456")

        assert res["platform"] == "flipkart"
        assert res["title"] == "Sample Product"
        assert res["current_price"] == 999.0
        assert res["original_price"] == 1999.0
        assert res["discount_percentage"] == 50.0
        assert res["rating"] == 4.2
        assert res["rating_count"] == 148271
        assert res["review_count"] == 12450
        assert res["currency"] == "INR"
        assert res["product_id"] == "SAMPLEPID123456"
        assert "image" in res
        assert "availability" in res
        assert "fetched_at" in res
        assert res["success"] is True


def test_rating_and_count_parsing():
    scraper = FlipkartScraper()

    # Rating test cases
    assert scraper.parse_rating("4.2 ★") == 4.2
    assert scraper.parse_rating("4.5 out of 5 stars") == 4.5
    assert scraper.parse_rating("3.9 / 5") == 3.9
    assert scraper.parse_rating("5.0") == 5.0
    assert scraper.parse_rating("0.0") == 0.0
    assert scraper.parse_rating("6.5") is None  # Out of range > 5.0
    assert scraper.parse_rating("No ratings yet") is None

    # Count test cases
    assert scraper.parse_count("1,48,271") == 148271
    assert scraper.parse_count("1.2 lakh") == 120000
    assert scraper.parse_count("2.5K") == 2500
    assert scraper.parse_count("10k") == 10000
    assert scraper.parse_count("1.5M") == 1500000
    assert scraper.parse_count("(1,450 Reviews)") == 1450
    assert scraper.parse_count("invalid") is None

    # Discount calculation
    assert scraper.calculate_discount(899.0, 1999.0) == 55.0
    assert scraper.calculate_discount(699.0, 1999.0) == 65.0
    assert scraper.calculate_discount(1000.0, 1000.0) is None
    assert scraper.calculate_discount(1200.0, 1000.0) is None


@pytest.mark.asyncio
async def test_amazon_metadata_extraction():
    mock_amazon_html = """
    <html>
    <head>
        <title>Amazon Product Page</title>
    </head>
    <body>
        <div id="dp-container">
            <h1 id="productTitle">Echo Dot (5th Gen) Smart Speaker</h1>
            <div id="corePrice_feature_div">
                <span class="a-price a-text-price"><span class="a-offscreen">₹5,499</span></span>
                <span class="a-price"><span class="a-offscreen">₹4,449</span></span>
                <span class="savingsPercentage">-19%</span>
            </div>
            <div id="acrPopover">
                <span class="a-size-base a-color-base">4.4</span>
            </div>
            <span id="acrCustomerReviewText">24,350 ratings</span>
            <img id="landingImage" data-old-hires="https://m.media-amazon.com/images/I/71echodot.jpg" />
        </div>
    </body>
    </html>
    """
    scraper = AmazonScraper()
    with patch("scrapers.playwright_manager.PlaywrightManager.fetch_html", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = (mock_amazon_html, "playwright")
        res = await scraper.extract_product("https://www.amazon.in/dp/B09B8V1LZ3")

        assert res.success is True
        assert res.title == "Echo Dot (5th Gen) Smart Speaker"
        assert res.current_price == 4449.0
        assert res.original_price == 5499.0
        assert res.discount_percentage == 19.0
        assert res.rating == 4.4
        assert res.rating_count == 24350
        assert res.currency == "INR"
        assert res.image_url == "https://m.media-amazon.com/images/I/71echodot.jpg"

