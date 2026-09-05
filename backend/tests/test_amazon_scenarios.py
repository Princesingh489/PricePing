import pytest
from scrapers.amazon_scraper import AmazonScraper
from db.models import PlatformEnum, AvailabilityEnum


@pytest.fixture
def amazon_scraper():
    return AmazonScraper()


AMAZON_SCENARIOS = [
    # 1. Electronics - Wireless Headphones
    {
        "url": "https://www.amazon.in/dp/B08N5WRWNW",
        "html": """
        <div id="dp-container">
            <span id="productTitle">Sony WH-1000XM4 Wireless Noise Cancelling Headphones</span>
            <div id="corePrice_desktop">
                <span class="a-price a-text-price"><span class="a-offscreen">₹29,990.00</span></span>
                <span class="a-price"><span class="a-offscreen">₹19,990.00</span></span>
                <span class="savingsPercentage">33%</span>
            </div>
            <img id="landingImage" src="https://m.media-amazon.com/images/I/71o8Q5XJS5L._SL1500_.jpg" />
            <span id="acrCustomerReviewText">14,820 ratings</span>
            <span data-hook="rating-out-of-text">4.6 out of 5 stars</span>
        </div>
        """,
        "expected_price": 19990.0,
        "expected_mrp": 29990.0,
        "expected_discount": 33.0,
        "expected_rating": 4.6,
        "expected_rating_count": 14820,
    },
    # 2. Smartphone with Variant (Storage/Color)
    {
        "url": "https://www.amazon.in/dp/B0BDK62PDX",
        "html": """
        <div id="dp-container">
            <span id="productTitle">Apple iPhone 14 (128 GB) - Blue</span>
            <div id="corePrice_feature_div">
                <span class="a-price a-text-price"><span class="a-offscreen">₹69,900.00</span></span>
                <span class="a-price"><span class="a-offscreen">₹58,999.00</span></span>
            </div>
            <img id="landingImage" data-old-hires="https://m.media-amazon.com/images/I/61bK6PMOC3L._SL1500_.jpg" src="thumb.jpg" />
            <span id="acrCustomerReviewText">8,450 ratings</span>
            <span data-hook="rating-out-of-text">4.5 out of 5 stars</span>
        </div>
        """,
        "expected_price": 58999.0,
        "expected_mrp": 69900.0,
        "expected_discount": 16.0,
        "expected_rating": 4.5,
        "expected_rating_count": 8450,
    },
    # 3. Laptop with Strikethrough MRP
    {
        "url": "https://www.amazon.in/dp/B0CX21C2B2",
        "html": """
        <div id="dp-container">
            <span id="productTitle">ASUS TUF Gaming F15 Intel Core i5 11th Gen</span>
            <div id="corePrice_desktop">
                <span class="a-price a-text-price"><span class="a-offscreen">₹74,990.00</span></span>
                <span class="a-price"><span class="a-offscreen">₹49,990.00</span></span>
            </div>
            <img id="landingImage" src="https://m.media-amazon.com/images/I/81xU9d8fGXL._SL1500_.jpg" />
            <span id="acrCustomerReviewText">3,120 ratings</span>
            <span data-hook="rating-out-of-text">4.3 out of 5</span>
        </div>
        """,
        "expected_price": 49990.0,
        "expected_mrp": 74990.0,
        "expected_discount": 33.0,
        "expected_rating": 4.3,
        "expected_rating_count": 3120,
    },
    # 4. Smartwatch with Savings %
    {
        "url": "https://www.amazon.in/dp/B0B3CQBRB4",
        "html": """
        <div id="dp-container">
            <span id="productTitle">Noise ColorFit Pulse 2 Max Smart Watch</span>
            <div id="corePrice_desktop">
                <span class="a-price a-text-price"><span class="a-offscreen">₹5,999.00</span></span>
                <span class="a-price"><span class="a-offscreen">₹1,199.00</span></span>
                <span class="savingsPercentage">80%</span>
            </div>
            <img id="landingImage" src="https://m.media-amazon.com/images/I/61SSVxTSs3L._SL1500_.jpg" />
            <span id="acrCustomerReviewText">42,390 ratings</span>
            <span data-hook="rating-out-of-text">4.0 out of 5 stars</span>
        </div>
        """,
        "expected_price": 1199.0,
        "expected_mrp": 5999.0,
        "expected_discount": 80.0,
        "expected_rating": 4.0,
        "expected_rating_count": 42390,
    },
    # 5. Fashion - Men T-Shirt
    {
        "url": "https://www.amazon.in/dp/B07YY1XZ21",
        "html": """
        <div id="dp-container">
            <span id="productTitle">Allen Solly Men's Regular Fit Polo</span>
            <div id="corePrice_desktop">
                <span class="a-price a-text-price"><span class="a-offscreen">₹1,099.00</span></span>
                <span class="a-price"><span class="a-offscreen">₹549.00</span></span>
            </div>
            <img id="landingImage" src="https://m.media-amazon.com/images/I/71dBjZ9JtSL._UL1500_.jpg" />
            <span id="acrCustomerReviewText">12,100 ratings</span>
            <span data-hook="rating-out-of-text">4.1 out of 5 stars</span>
        </div>
        """,
        "expected_price": 549.0,
        "expected_mrp": 1099.0,
        "expected_discount": 50.0,
        "expected_rating": 4.1,
        "expected_rating_count": 12100,
    },
    # 6. Fashion - Women Kurti
    {
        "url": "https://www.amazon.in/dp/B08XX92LKP",
        "html": """
        <div id="dp-container">
            <span id="productTitle">BIBA Women Cotton Straight Kurta</span>
            <div id="corePrice_desktop">
                <span class="a-price a-text-price"><span class="a-offscreen">₹2,499.00</span></span>
                <span class="a-price"><span class="a-offscreen">₹999.00</span></span>
            </div>
            <img id="landingImage" src="https://m.media-amazon.com/images/I/81x12KKL._UL1500_.jpg" />
            <span id="acrCustomerReviewText">1,450 ratings</span>
            <span data-hook="rating-out-of-text">4.2 out of 5 stars</span>
        </div>
        """,
        "expected_price": 999.0,
        "expected_mrp": 2499.0,
        "expected_discount": 60.0,
        "expected_rating": 4.2,
        "expected_rating_count": 1450,
    },
    # 7. Footwear - Running Shoes
    {
        "url": "https://www.amazon.in/dp/B09Z1Y2X3W",
        "html": """
        <div id="dp-container">
            <span id="productTitle">Puma Men's Dazzler Running Shoes</span>
            <div id="corePrice_desktop">
                <span class="a-price a-text-price"><span class="a-offscreen">₹3,999.00</span></span>
                <span class="a-price"><span class="a-offscreen">₹1,599.00</span></span>
            </div>
            <img id="landingImage" src="https://m.media-amazon.com/images/I/71ZtV8Zf1zL._UL1500_.jpg" />
            <span id="acrCustomerReviewText">5,620 ratings</span>
            <span data-hook="rating-out-of-text">4.1 out of 5 stars</span>
        </div>
        """,
        "expected_price": 1599.0,
        "expected_mrp": 3999.0,
        "expected_discount": 60.0,
        "expected_rating": 4.1,
        "expected_rating_count": 5620,
    },
    # 8. Home & Kitchen - Air Fryer
    {
        "url": "https://www.amazon.in/dp/B0988XX881",
        "html": """
        <div id="dp-container">
            <span id="productTitle">Philips Digital Air Fryer HD9252/90</span>
            <div id="corePrice_desktop">
                <span class="a-price a-text-price"><span class="a-offscreen">₹11,995.00</span></span>
                <span class="a-price"><span class="a-offscreen">₹7,999.00</span></span>
            </div>
            <img id="landingImage" src="https://m.media-amazon.com/images/I/61nK8vJ5kFL._SL1500_.jpg" />
            <span id="acrCustomerReviewText">6,890 ratings</span>
            <span data-hook="rating-out-of-text">4.4 out of 5 stars</span>
        </div>
        """,
        "expected_price": 7999.0,
        "expected_mrp": 11995.0,
        "expected_discount": 33.0,
        "expected_rating": 4.4,
        "expected_rating_count": 6890,
    },
    # 9. Books - Paperback
    {
        "url": "https://www.amazon.in/dp/1847941834",
        "html": """
        <div id="dp-container">
            <span id="productTitle">Atomic Habits by James Clear</span>
            <div id="corePrice_desktop">
                <span class="a-price a-text-price"><span class="a-offscreen">₹799.00</span></span>
                <span class="a-price"><span class="a-offscreen">₹499.00</span></span>
            </div>
            <img id="landingImage" src="https://m.media-amazon.com/images/I/81F90H7hnML._SL1500_.jpg" />
            <span id="acrCustomerReviewText">98,240 ratings</span>
            <span data-hook="rating-out-of-text">4.7 out of 5 stars</span>
        </div>
        """,
        "expected_price": 499.0,
        "expected_mrp": 799.0,
        "expected_discount": 38.0,
        "expected_rating": 4.7,
        "expected_rating_count": 98240,
    },
    # 10. Beauty - Shampoo
    {
        "url": "https://www.amazon.in/dp/B07R45KKL1",
        "html": """
        <div id="dp-container">
            <span id="productTitle">L'Oreal Paris Total Repair 5 Shampoo, 1000ml</span>
            <div id="corePrice_desktop">
                <span class="a-price a-text-price"><span class="a-offscreen">₹1,099.00</span></span>
                <span class="a-price"><span class="a-offscreen">₹769.00</span></span>
            </div>
            <img id="landingImage" src="https://m.media-amazon.com/images/I/61K-K0GqG0L._SL1500_.jpg" />
            <span id="acrCustomerReviewText">18,300 ratings</span>
            <span data-hook="rating-out-of-text">4.3 out of 5 stars</span>
        </div>
        """,
        "expected_price": 769.0,
        "expected_mrp": 1099.0,
        "expected_discount": 30.0,
        "expected_rating": 4.3,
        "expected_rating_count": 18300,
    },
    # 11. Deal Price Tag (#priceblock_dealprice)
    {
        "url": "https://www.amazon.in/dp/B08N5N6RSS",
        "html": """
        <div id="dp-container">
            <span id="productTitle">Logitech G29 Driving Force Racing Wheel</span>
            <span id="priceblock_dealprice">₹24,990.00</span>
            <span class="a-price a-text-price"><span class="a-offscreen">₹39,995.00</span></span>
            <img id="landingImage" src="https://m.media-amazon.com/images/I/61m1a0YhZ7L._SL1500_.jpg" />
            <span id="acrCustomerReviewText">3,400 ratings</span>
            <span data-hook="rating-out-of-text">4.6 out of 5 stars</span>
        </div>
        """,
        "expected_price": 24990.0,
        "expected_mrp": 39995.0,
        "expected_discount": 38.0,
        "expected_rating": 4.6,
        "expected_rating_count": 3400,
    },
    # 12. Grocery - Green Tea
    {
        "url": "https://www.amazon.in/dp/B00T75F9OO",
        "html": """
        <div id="dp-container">
            <span id="productTitle">Tetley Green Tea Lemon and Honey, 100 Bags</span>
            <div id="corePrice_desktop">
                <span class="a-price a-text-price"><span class="a-offscreen">₹520.00</span></span>
                <span class="a-price"><span class="a-offscreen">₹416.00</span></span>
            </div>
            <img id="landingImage" src="https://m.media-amazon.com/images/I/81xU9d8fGXL._SL1500_.jpg" />
            <span id="acrCustomerReviewText">8,900 ratings</span>
            <span data-hook="rating-out-of-text">4.4 out of 5 stars</span>
        </div>
        """,
        "expected_price": 416.0,
        "expected_mrp": 520.0,
        "expected_discount": 20.0,
        "expected_rating": 4.4,
        "expected_rating_count": 8900,
    },
    # 13. JSON-LD structured product with offers
    {
        "url": "https://www.amazon.in/dp/B07HGJKD81",
        "html": """
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "OnePlus Nord CE 3 Lite 5G (Pastel Lime, 8GB RAM, 128GB)",
            "image": "https://m.media-amazon.com/images/I/61QRgOgBx0L._SL1500_.jpg",
            "offers": {
                "@type": "Offer",
                "price": "17499.00",
                "highPrice": "19999.00",
                "priceCurrency": "INR",
                "availability": "https://schema.org/InStock"
            },
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": "4.2",
                "ratingCount": "32100"
            }
        }
        </script>
        <div id="dp-container">
            <span id="productTitle">OnePlus Nord CE 3 Lite 5G</span>
            <div id="corePrice_desktop">
                <span class="a-price"><span class="a-offscreen">₹17,499.00</span></span>
            </div>
        </div>
        """,
        "expected_price": 17499.0,
        "expected_mrp": 19999.0,
        "expected_discount": 13.0,
        "expected_rating": 4.2,
        "expected_rating_count": 32100,
    },
    # 14. Product with Bank Offers (Ensure bank discount ₹1,500 is not picked as selling price)
    {
        "url": "https://www.amazon.in/dp/B08L5WHZ99",
        "html": """
        <div id="dp-container">
            <span id="productTitle">Samsung Galaxy Tab S9 FE</span>
            <div id="corePrice_desktop">
                <span class="a-price a-text-price"><span class="a-offscreen">₹44,999.00</span></span>
                <span class="a-price"><span class="a-offscreen">₹34,999.00</span></span>
            </div>
            <div class="bank-offers-section">
                <span>Bank Offer: Instant discount of ₹4,000 on HDFC Bank Cards</span>
            </div>
            <img id="landingImage" src="https://m.media-amazon.com/images/I/51b98X.jpg" />
        </div>
        """,
        "expected_price": 34999.0,
        "expected_mrp": 44999.0,
        "expected_discount": 22.0,
    },
    # 15. Product with Coupon Section (Ensure coupon ₹50 is not picked as price)
    {
        "url": "https://www.amazon.in/dp/B07W95K91X",
        "html": """
        <div id="dp-container">
            <span id="productTitle">Portronics Toad 23 Wireless Mouse</span>
            <div id="corePrice_desktop">
                <span class="a-price a-text-price"><span class="a-offscreen">₹599.00</span></span>
                <span class="a-price"><span class="a-offscreen">₹299.00</span></span>
            </div>
            <div id="couponSection">
                <label>Apply ₹30 coupon. Terms apply.</label>
            </div>
            <img id="landingImage" src="https://m.media-amazon.com/images/I/61Toad.jpg" />
        </div>
        """,
        "expected_price": 299.0,
        "expected_mrp": 599.0,
        "expected_discount": 50.0,
    },
    # 16. Product with EMI section (Ensure EMI ₹120/mo is rejected)
    {
        "url": "https://www.amazon.in/dp/B08X46KKP1",
        "html": """
        <div id="dp-container">
            <span id="productTitle">Bajaj Splendora 3 Litre Instant Water Heater</span>
            <div id="corePrice_desktop">
                <span class="a-price a-text-price"><span class="a-offscreen">₹5,880.00</span></span>
                <span class="a-price"><span class="a-offscreen">₹2,699.00</span></span>
            </div>
            <div class="emi-details">
                <span>EMI starts at ₹131/month. No Cost EMI available</span>
            </div>
            <img id="landingImage" src="https://m.media-amazon.com/images/I/71Heater.jpg" />
        </div>
        """,
        "expected_price": 2699.0,
        "expected_mrp": 5880.0,
        "expected_discount": 54.0,
    },
    # 17. Product with Exchange Offer (Ensure exchange ₹12,000 is rejected)
    {
        "url": "https://www.amazon.in/dp/B09G9FPHY6",
        "html": """
        <div id="dp-container">
            <span id="productTitle">Apple iPad 10.2-inch (9th Gen)</span>
            <div id="corePrice_desktop">
                <span class="a-price a-text-price"><span class="a-offscreen">₹32,900.00</span></span>
                <span class="a-price"><span class="a-offscreen">₹27,990.00</span></span>
            </div>
            <div id="exchangePackage">
                <span>Up to ₹14,000 off on exchange</span>
            </div>
            <img id="landingImage" src="https://m.media-amazon.com/images/I/61ipad.jpg" />
        </div>
        """,
        "expected_price": 27990.0,
        "expected_mrp": 32900.0,
        "expected_discount": 15.0,
    },
    # 18. Product Out of Stock
    {
        "url": "https://www.amazon.in/dp/B07VGRJDFY",
        "html": """
        <div id="dp-container">
            <span id="productTitle">Limited Edition Collector Keyboard</span>
            <div id="corePrice_desktop">
                <span class="a-price"><span class="a-offscreen">₹8,499.00</span></span>
            </div>
            <div id="availability">
                <span>Currently unavailable. We don't know when or if this item will be back in stock.</span>
            </div>
            <img id="landingImage" src="https://m.media-amazon.com/images/I/71kb.jpg" />
        </div>
        """,
        "expected_price": 8499.0,
        "expected_availability": AvailabilityEnum.out_of_stock,
    },
    # 19. Product with High Ratings Count (e.g. 1,48,271)
    {
        "url": "https://www.amazon.in/dp/B01LW7MQ64",
        "html": """
        <div id="dp-container">
            <span id="productTitle">SanDisk Ultra Dual Drive Go Type-C 64GB</span>
            <div id="corePrice_desktop">
                <span class="a-price a-text-price"><span class="a-offscreen">₹1,350.00</span></span>
                <span class="a-price"><span class="a-offscreen">₹799.00</span></span>
            </div>
            <span id="acrCustomerReviewText">1,48,271 ratings</span>
            <span data-hook="rating-out-of-text">4.3 out of 5 stars</span>
            <img id="landingImage" src="https://m.media-amazon.com/images/I/61pendrive.jpg" />
        </div>
        """,
        "expected_price": 799.0,
        "expected_mrp": 1350.0,
        "expected_rating": 4.3,
        "expected_rating_count": 148271,
    },
    # 20. Product without MRP (current price = MRP, no discount)
    {
        "url": "https://www.amazon.in/dp/B08XYZ1234",
        "html": """
        <div id="dp-container">
            <span id="productTitle">Custom Handmade Coffee Mug</span>
            <div id="corePrice_desktop">
                <span class="a-price"><span class="a-offscreen">₹450.00</span></span>
            </div>
            <img id="landingImage" src="https://m.media-amazon.com/images/I/61mug.jpg" />
        </div>
        """,
        "expected_price": 450.0,
        "expected_mrp": None,
        "expected_discount": None,
    },
]


@pytest.mark.parametrize("scenario", AMAZON_SCENARIOS)
def test_amazon_20_scenarios(amazon_scraper, scenario):
    res = amazon_scraper.extract_from_html(scenario["html"], scenario["url"])
    assert res.success is True
    assert res.current_price == scenario["expected_price"]

    if "expected_mrp" in scenario:
        assert res.original_price == scenario["expected_mrp"]
    if "expected_discount" in scenario:
        assert res.discount_percentage == scenario["expected_discount"]
    if "expected_rating" in scenario:
        assert res.rating == scenario["expected_rating"]
    if "expected_rating_count" in scenario:
        assert res.rating_count == scenario["expected_rating_count"]
    if "expected_availability" in scenario:
        assert res.availability == scenario["expected_availability"]
