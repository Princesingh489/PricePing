"""
Comprehensive Universal AJIO Test Suite
========================================
Validates extraction across all AJIO product categories:
1. Apparel with ProductGroup + hasVariant (e.g. Point Cove Shirt)
2. Electronics/Gadgets with Product schema
3. Footwear with UK size synchronization
4. Pure window.__PRELOADED_STATE__ extraction
5. Out-of-stock product handling
6. Domain and URL pattern detection
"""
import pytest
from scrapers.ajio.scraper import AjioScraper
from scrapers.scraper_router import detect_platform_from_url
from db.models import PlatformEnum, AvailabilityEnum


@pytest.fixture
def scraper():
    return AjioScraper()


def test_ajio_url_variations(scraper):
    urls = [
        ("https://www.ajio.com/point-cove-shirt/p/443666961_olive?user=old&", "443666961_olive"),
        ("https://m.ajio.com/p/460788224_black", "460788224_black"),
        ("https://ajio.in/shoes/p/469123456", "469123456"),
        ("https://www.ajio.com/clothing/p/460123456_blue#details", "460123456_blue"),
        ("https://www.ajio.com/search/?productCode=469999111_red", "469999111_red"),
    ]
    for u, expected_id in urls:
        assert detect_platform_from_url(u) == PlatformEnum.ajio
        assert scraper.extract_product_id(u) == expected_id


def test_ajio_apparel_product_group(scraper):
    """Test clothing with ProductGroup schema and hasVariant arrays."""
    html = """
    <html>
    <head>
        <title>Point Cove Boys Shirt | Ajio.com</title>
        <script type="application/ld+json">
        {
            "@context": "http://schema.org/",
            "@type": "ProductGroup",
            "name": "Boys Patterned Relaxed Fit Shirt with Patch Pocket",
            "brand": {"@type": "Thing", "name": "POINT COVE"},
            "image": "https://assets.ajio.com/shirt.jpg",
            "offers": {
                "@type": "Offer",
                "price": "305",
                "priceCurrency": "INR",
                "availability": "https://schema.org/InStock"
            },
            "hasVariant": [
                {
                    "@type": "Product",
                    "name": "Boys Patterned Relaxed Fit Shirt - 7-8Y",
                    "size": "7-8Y",
                    "sku": "443666961003",
                    "offers": {
                        "price": 305,
                        "highPrice": 599,
                        "availability": "https://schema.org/InStock"
                    }
                },
                {
                    "@type": "Product",
                    "name": "Boys Patterned Relaxed Fit Shirt - 9-10Y",
                    "size": "9-10Y",
                    "sku": "443666961004",
                    "offers": {
                        "price": 356,
                        "highPrice": 699,
                        "availability": "https://schema.org/InStock"
                    }
                }
            ]
        }
        </script>
    </head>
    <body>
        <div id="appContainer"></div>
    </body>
    </html>
    """
    url = "https://www.ajio.com/point-cove-boys-patterned-relaxed-fit-shirt-with-patch-pocket/p/443666961_olive"
    res = scraper.extract_from_html(html, url)
    assert res.success is True
    assert "POINT COVE" in res.title
    assert "Boys Patterned Relaxed Fit Shirt" in res.title
    assert res.brand == "POINT COVE"
    assert res.current_price == 305.0
    assert res.original_price == 599.0
    assert res.confidence_score >= 80
    assert len(res.variants) == 2

    # Test size sync for 9-10Y
    url_size = f"{url}?size=9-10Y"
    synced = scraper.sync_variant_price(res, url_size)
    assert synced.current_price == 356.0
    assert synced.original_price == 699.0


def test_ajio_electronics_product_schema(scraper):
    """Test electronics/gadgets using Product schema."""
    html = """
    <html>
    <head>
        <title>boAt Rockerz 450 Bluetooth Headphones | Ajio.com</title>
        <script type="application/ld+json">
        {
            "@context": "http://schema.org/",
            "@type": "Product",
            "name": "Rockerz 450 On-Ear Wireless Headphones",
            "brand": "boAt",
            "image": "https://assets.ajio.com/boat450.jpg",
            "offers": {
                "@type": "Offer",
                "price": "1499",
                "highPrice": "3990",
                "priceCurrency": "INR",
                "availability": "https://schema.org/InStock"
            },
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": "4.3",
                "ratingCount": "1250"
            }
        }
        </script>
    </head>
    <body><div id="app"></div></body>
    </html>
    """
    url = "https://www.ajio.com/boat-rockerz-450/p/469012345_black"
    res = scraper.extract_from_html(html, url)
    assert res.success is True
    assert res.brand == "boAt"
    assert res.current_price == 1499.0
    assert res.original_price == 3990.0
    assert res.rating == 4.3
    assert res.rating_count == 1250


def test_ajio_pure_preloaded_state(scraper):
    """Test extraction from window.__PRELOADED_STATE__ with zero visible DOM."""
    html = """
    <html>
    <head><title>AJIO Online Shopping</title></head>
    <body>
        <div id="app"></div>
        <script>
        window.__PRELOADED_STATE__ = {
            "product": {
                "productDetails": {
                    "name": "Men Slim Fit Washed Jeans",
                    "brandName": "LEVIS",
                    "price": {"value": 1899, "discountValue": 50},
                    "wasPriceData": {"value": 3799},
                    "images": [{"url": "https://assets.ajio.com/levis.jpg"}],
                    "fnlColorVariantData": {"color": "Blue"}
                }
            }
        };
        </script>
    </body>
    </html>
    """
    url = "https://www.ajio.com/levis-jeans/p/461234888_blue"
    res = scraper.extract_from_html(html, url)
    assert res.success is True
    assert "LEVIS" in res.title
    assert res.brand == "LEVIS"
    assert res.current_price == 1899.0
    assert res.original_price == 3799.0
    assert res.discount_percentage == 50.0
    assert res.image_url == "https://assets.ajio.com/levis.jpg"


def test_ajio_out_of_stock_product(scraper):
    """Test out of stock extraction handling."""
    html = """
    <div class="prod-content">
        <h2 class="brand-name">PUMA</h2>
        <h1 class="prod-title">Men Smash V2 Sneakers</h1>
        <div class="prod-sp">₹2,499</div>
        <span class="prod-cp">₹4,999</span>
        <div class="out-of-stock">Currently Out of Stock</div>
    </div>
    """
    url = "https://www.ajio.com/puma-sneakers/p/460987654_white"
    res = scraper.extract_from_html(html, url)
    assert res.success is True
    assert res.current_price == 2499.0
    assert res.availability == AvailabilityEnum.out_of_stock


def test_ajio_opengraph_fallback(scraper):
    """Test OpenGraph meta tags fallback when scripts are absent."""
    html = """
    <html>
    <head>
        <meta property="og:title" content="WROGN Men Checked Casual Shirt" />
        <meta property="product:brand" content="WROGN" />
        <meta property="product:price:amount" content="899" />
        <meta property="product:original_price:amount" content="2199" />
        <meta property="og:image" content="https://assets.ajio.com/wrogn.jpg" />
    </head>
    <body><div class="prod-content"></div></body>
    </html>
    """
    url = "https://www.ajio.com/wrogn-shirt/p/460555666_navy"
    res = scraper.extract_from_html(html, url)
    assert res.success is True
    assert "WROGN" in res.title
    assert res.current_price == 899.0
    assert res.original_price == 2199.0
    assert res.image_url == "https://assets.ajio.com/wrogn.jpg"
