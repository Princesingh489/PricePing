"""
Automated Test Suite for Overhauled Scraping Engine Components:
1. URL Normalizer (Variant Targeting & Tracking Stripping)
2. Playwright Route Optimizer (Network & Tracker Interception)
3. React/SSR Hidden JSON State Extractor (Next.js & Myntra window.__myx)
4. Decoupled Product Creation & Status Tracking
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from scrapers.normalizers import ECommerceURLNormalizer, NormalizedURLResult
from scrapers.playwright_optimizer import (
    BLOCKED_RESOURCE_TYPES,
    BLOCKED_ANALYTICS_DOMAINS,
    intercept_and_filter_requests
)
from scrapers.extractors.json_state_extractor import (
    extract_react_state_from_html,
    clean_price_value,
    ExtractedVariantData
)


# =========================================================================
# 1. URL Normalizer Tests
# =========================================================================

def test_amazon_url_normalizer_asin_and_variant():
    url = "https://www.amazon.in/boAt-Rockerz-550-Over-Ear-Wireless/dp/B0856HNMR7/ref=sr_1_1?crid=123&keywords=boat&qid=1600000&sprefix=boat%2Caps%2C200&sr=8-1&th=1"
    res = ECommerceURLNormalizer.normalize_amazon(url)

    assert res.platform == "amazon"
    assert res.product_id == "B0856HNMR7"
    assert res.variant_id == "B0856HNMR7"
    assert "https://www.amazon.in/dp/B0856HNMR7" in res.canonical_url
    assert "th=1" in res.canonical_url
    assert "psc=1" in res.canonical_url
    assert "ref=" not in res.canonical_url
    assert "keywords=" not in res.canonical_url


def test_flipkart_url_normalizer_pid_and_clean_path():
    url = (
        "https://www.flipkart.com/apple-iphone-15-black-128-gb/p/itm6ac6485515ae4"
        "?pid=MOBGTAGPTB3VS24W&lid=LSTMOBGTAGPTB3VS24WVUQOXF&marketplace=FLIPKART"
        "&store=tyy%2F4io&srno=s_1_1&otracker=search&fm=organic"
    )
    res = ECommerceURLNormalizer.normalize_flipkart(url)

    assert res.platform == "flipkart"
    assert res.product_id == "MOBGTAGPTB3VS24W"
    assert "pid=MOBGTAGPTB3VS24W" in res.canonical_url
    assert "lid=LSTMOBGTAGPTB3VS24WVUQOXF" in res.canonical_url
    assert "otracker=" not in res.canonical_url
    assert "marketplace=" not in res.canonical_url
    assert "srno=" not in res.canonical_url


def test_myntra_url_normalizer_style_and_size():
    url = (
        "https://www.myntra.com/shirts/roadster/roadster-men-navy-blue-casual-shirt/24567890/buy"
        "?size=40&skuId=1029384&utm_source=google&utm_medium=cpc&rawQuery=shirt"
    )
    res = ECommerceURLNormalizer.normalize_myntra(url)

    assert res.platform == "myntra"
    assert res.product_id == "24567890"
    assert "size=40" in res.canonical_url
    assert "skuId=1029384" in res.canonical_url
    assert "utm_source" not in res.canonical_url
    assert "rawQuery" not in res.canonical_url


def test_url_normalizer_dispatcher():
    res_amz = ECommerceURLNormalizer.normalize("https://www.amazon.in/dp/B09XYZ1234?tag=affiliate")
    res_fk = ECommerceURLNormalizer.normalize("https://www.flipkart.com/product/p/itm123?pid=XYZ987")
    res_myntra = ECommerceURLNormalizer.normalize("https://www.myntra.com/brand/product/12345678/buy")

    assert res_amz.platform == "amazon"
    assert res_fk.platform == "flipkart"
    assert res_myntra.platform == "myntra"


# =========================================================================
# 2. Playwright Route Optimizer Tests
# =========================================================================

@pytest.mark.asyncio
async def test_route_interceptor_aborts_blocked_resource_types():
    for resource_type in ["image", "media", "font", "stylesheet", "websocket"]:
        mock_route = AsyncMock()
        mock_request = MagicMock()
        mock_request.resource_type = resource_type
        mock_request.url = "https://example.com/assets/style.css"

        await intercept_and_filter_requests(mock_route, mock_request)
        mock_route.abort.assert_awaited_once()
        mock_route.continue_.assert_not_called()


@pytest.mark.asyncio
async def test_route_interceptor_aborts_analytics_domains():
    for domain in ["https://www.google-analytics.com/analytics.js", "https://connect.facebook.net/en_US/fbevents.js", "https://static.criteo.net/ld.js"]:
        mock_route = AsyncMock()
        mock_request = MagicMock()
        mock_request.resource_type = "script"
        mock_request.url = domain

        await intercept_and_filter_requests(mock_route, mock_request)
        mock_route.abort.assert_awaited_once()
        mock_route.continue_.assert_not_called()


@pytest.mark.asyncio
async def test_route_interceptor_allows_essential_html_and_api():
    mock_route = AsyncMock()
    mock_request = MagicMock()
    mock_request.resource_type = "document"
    mock_request.url = "https://www.myntra.com/12345/buy"

    await intercept_and_filter_requests(mock_route, mock_request)
    mock_route.continue_.assert_awaited_once()
    mock_route.abort.assert_not_called()


# =========================================================================
# 3. JSON State Extractor Tests
# =========================================================================

def test_clean_price_value():
    assert clean_price_value("₹1,499.00") == 1499.0
    assert clean_price_value("Rs. 25,000") == 25000.0
    assert clean_price_value(999) == 999.0
    assert clean_price_value(None) is None


def test_extract_myntra_window_myx_state():
    mock_html = """
    <!DOCTYPE html>
    <html>
    <head><title>Myntra Test Product</title></head>
    <body>
        <script>
            window.__myx = {
                "pdpData": {
                    "name": "Men Slim Fit Casual Shirt",
                    "brand": {"name": "Roadster"},
                    "price": {
                        "discounted": 799,
                        "mrp": 1999
                    },
                    "media": {
                        "albums": [
                            {"images": [{"src": "https://assets.myntassets.com/h_1440,q_90/v1/product.jpg"}]}
                        ]
                    },
                    "sizes": [
                        {"label": "S", "skuId": 101, "available": true, "discountedPrice": 799, "mrp": 1999},
                        {"label": "M", "skuId": 102, "available": true, "discountedPrice": 849, "mrp": 1999},
                        {"label": "L", "skuId": 103, "available": false, "discountedPrice": 799, "mrp": 1999}
                    ]
                }
            };
        </script>
    </body>
    </html>
    """

    # Test targeted size "M"
    extracted_m = extract_react_state_from_html(mock_html, target_variant_id="M")
    assert "Roadster" in extracted_m.title
    assert extracted_m.price == 849.0
    assert extracted_m.original_price == 1999.0
    assert extracted_m.size == "M"
    assert extracted_m.is_in_stock is True
    assert "myntassets.com" in extracted_m.image_url


def test_extract_nextjs_data_state():
    mock_html = """
    <!DOCTYPE html>
    <html>
    <body>
        <script id="__NEXT_DATA__" type="application/json">
        {
            "props": {
                "pageProps": {
                    "product": {
                        "title": "Wireless Earbuds with Active Noise Cancellation",
                        "price": 2499.0,
                        "originalPrice": 4999.0,
                        "imageUrl": "https://cdn.example.com/earbuds.jpg",
                        "inStock": true,
                        "variants": [
                            {"id": "black-anc", "size": "Standard", "price": 2499.0}
                        ]
                    }
                }
            }
        }
        </script>
    </body>
    </html>
    """
    data = extract_react_state_from_html(mock_html, target_variant_id="black-anc")
    assert "Wireless Earbuds" in data.title
    assert data.price == 2499.0
    assert data.original_price == 4999.0
    assert data.is_in_stock is True
    assert data.size == "Standard"
