import pytest
from scrapers.myntra_scraper import MyntraScraper
from db.models import PlatformEnum, AvailabilityEnum


@pytest.fixture
def myntra_scraper():
    return MyntraScraper()


MYNTRA_SCENARIOS = [
    # 1. Men T-Shirt
    {
        "url": "https://www.myntra.com/tshirts/roadster/roadster-men-black-cotton-pure-cotton-t-shirt/1234567/buy",
        "html": """
        <div class="pdp-details">
            <h1 class="pdp-title">Roadster</h1>
            <h1 class="pdp-name">Men Pure Cotton T-shirt</h1>
            <span class="pdp-price">₹399</span>
            <span class="pdp-mrp">₹999</span>
            <span class="pdp-discount">(60% OFF)</span>
            <div class="index-overallRating"><div>4.2</div></div>
            <div class="index-ratingsCount">15.4k Ratings</div>
            <img class="image-grid-image" src="https://assets.myntassets.com/h_1440,q_90,w_1080/v1/assets/images/123.jpg" />
        </div>
        """,
        "expected_price": 399.0,
        "expected_mrp": 999.0,
        "expected_discount": 60.0,
        "expected_rating": 4.2,
        "expected_rating_count": 15400,
    },
    # 2. Women Dress
    {
        "url": "https://www.myntra.com/dresses/tokyo-talkies/tokyo-talkies-women-green-floral-printed-fit-and-flare-dress/2233445/buy",
        "html": """
        <div class="pdp-details">
            <h1 class="pdp-title">Tokyo Talkies</h1>
            <h1 class="pdp-name">Floral Print Fit & Flare Dress</h1>
            <span class="pdp-price">₹689</span>
            <span class="pdp-mrp">₹2,299</span>
            <span class="pdp-discount">(70% OFF)</span>
            <div class="index-overallRating"><div>4.1</div></div>
            <div class="index-ratingsCount">8,200 Ratings</div>
            <img class="image-grid-image" src="https://assets.myntassets.com/dresses/2233.jpg" />
        </div>
        """,
        "expected_price": 689.0,
        "expected_mrp": 2299.0,
        "expected_discount": 70.0,
        "expected_rating": 4.1,
        "expected_rating_count": 8200,
    },
    # 3. Footwear - Sneakers
    {
        "url": "https://www.myntra.com/casual-shoes/puma/puma-smash-v2-l-sneakers/3344556/buy",
        "html": """
        <div class="pdp-details">
            <h1 class="pdp-title">Puma</h1>
            <h1 class="pdp-name">Smash v2 L Leather Sneakers</h1>
            <span class="pdp-price">₹2,249</span>
            <span class="pdp-mrp">₹4,499</span>
            <span class="pdp-discount">(50% OFF)</span>
            <div class="index-overallRating"><div>4.3</div></div>
            <div class="index-ratingsCount">5,600 Ratings</div>
            <img class="image-grid-image" src="https://assets.myntassets.com/shoes/puma.jpg" />
        </div>
        """,
        "expected_price": 2249.0,
        "expected_mrp": 4499.0,
        "expected_discount": 50.0,
        "expected_rating": 4.3,
        "expected_rating_count": 5600,
    },
    # 4. Handbag
    {
        "url": "https://www.myntra.com/handbags/lavie/lavie-women-structured-tote-bag/4455667/buy",
        "html": """
        <div class="pdp-details">
            <h1 class="pdp-title">Lavie</h1>
            <h1 class="pdp-name">Structured Tote Bag</h1>
            <span class="pdp-price">₹1,199</span>
            <span class="pdp-mrp">₹3,999</span>
            <span class="pdp-discount">(70% OFF)</span>
            <img class="image-grid-image" src="https://assets.myntassets.com/bag/lavie.jpg" />
        </div>
        """,
        "expected_price": 1199.0,
        "expected_mrp": 3999.0,
        "expected_discount": 70.0,
    },
    # 5. Jeans
    {
        "url": "https://www.myntra.com/jeans/highlander/highlander-men-tapered-fit-jeans/5566778/buy",
        "html": """
        <div class="pdp-details">
            <h1 class="pdp-title">HIGHLANDER</h1>
            <h1 class="pdp-name">Men Slim Tapered Jeans</h1>
            <span class="pdp-price">₹799</span>
            <span class="pdp-mrp">₹1,999</span>
            <span class="pdp-discount">(60% OFF)</span>
            <img class="image-grid-image" src="https://assets.myntassets.com/jeans/highlander.jpg" />
        </div>
        """,
        "expected_price": 799.0,
        "expected_mrp": 1999.0,
        "expected_discount": 60.0,
    },
    # 6. Jacket
    {
        "url": "https://www.myntra.com/jackets/fort-collins/fort-collins-men-bomber-jacket/6677889/buy",
        "html": """
        <div class="pdp-details">
            <h1 class="pdp-title">Fort Collins</h1>
            <h1 class="pdp-name">Padded Bomber Jacket</h1>
            <span class="pdp-price">₹1,499</span>
            <span class="pdp-mrp">₹3,499</span>
            <span class="pdp-discount">(57% OFF)</span>
            <img class="image-grid-image" src="https://assets.myntassets.com/jacket/fc.jpg" />
        </div>
        """,
        "expected_price": 1499.0,
        "expected_mrp": 3499.0,
        "expected_discount": 57.0,
    },
    # 7. Sunglasses
    {
        "url": "https://www.myntra.com/sunglasses/voyage/voyage-unisex-aviator-sunglasses/7788990/buy",
        "html": """
        <div class="pdp-details">
            <h1 class="pdp-title">Voyage</h1>
            <h1 class="pdp-name">Polarized Aviator Sunglasses</h1>
            <span class="pdp-price">₹849</span>
            <span class="pdp-mrp">₹2,500</span>
            <span class="pdp-discount">(66% OFF)</span>
            <img class="image-grid-image" src="https://assets.myntassets.com/glasses/v.jpg" />
        </div>
        """,
        "expected_price": 849.0,
        "expected_mrp": 2500.0,
        "expected_discount": 66.0,
    },
    # 8. Watch
    {
        "url": "https://www.myntra.com/watches/fossil/fossil-men-chronograph-watch/8899001/buy",
        "html": """
        <div class="pdp-details">
            <h1 class="pdp-title">Fossil</h1>
            <h1 class="pdp-name">Grant Chronograph Black Leather Watch</h1>
            <span class="pdp-price">₹7,495</span>
            <span class="pdp-mrp">₹12,495</span>
            <span class="pdp-discount">(40% OFF)</span>
            <img class="image-grid-image" src="https://assets.myntassets.com/watches/fossil.jpg" />
        </div>
        """,
        "expected_price": 7495.0,
        "expected_mrp": 12495.0,
        "expected_discount": 40.0,
    },
    # 9. Perfume
    {
        "url": "https://www.myntra.com/perfume/jaguar/jaguar-classic-black-edt-100ml/9900112/buy",
        "html": """
        <div class="pdp-details">
            <h1 class="pdp-title">Jaguar</h1>
            <h1 class="pdp-name">Classic Black Eau De Toilette 100ml</h1>
            <span class="pdp-price">₹1,960</span>
            <span class="pdp-mrp">₹3,500</span>
            <span class="pdp-discount">(44% OFF)</span>
            <img class="image-grid-image" src="https://assets.myntassets.com/perfume/jaguar.jpg" />
        </div>
        """,
        "expected_price": 1960.0,
        "expected_mrp": 3500.0,
        "expected_discount": 44.0,
    },
    # 10. Ethnic Kurta Set
    {
        "url": "https://www.myntra.com/kurta-sets/anouk/anouk-women-printed-kurta-with-palazzos/1011123/buy",
        "html": """
        <div class="pdp-details">
            <h1 class="pdp-title">Anouk</h1>
            <h1 class="pdp-name">Pure Cotton Kurta with Palazzos</h1>
            <span class="pdp-price">₹899</span>
            <span class="pdp-mrp">₹2,999</span>
            <span class="pdp-discount">(70% OFF)</span>
            <img class="image-grid-image" src="https://assets.myntassets.com/ethnic/anouk.jpg" />
        </div>
        """,
        "expected_price": 899.0,
        "expected_mrp": 2999.0,
        "expected_discount": 70.0,
    },
    # 11. Large Discount Clearance (80% off)
    {
        "url": "https://www.myntra.com/shirts/wrogn/wrogn-slim-fit-casual-shirt/1112134/buy",
        "html": """
        <div class="pdp-details">
            <h1 class="pdp-title">WROGN</h1>
            <h1 class="pdp-name">Men Slim Casual Shirt</h1>
            <span class="pdp-price">₹519</span>
            <span class="pdp-mrp">₹2,599</span>
            <span class="pdp-discount">(80% OFF)</span>
            <img class="image-grid-image" src="https://assets.myntassets.com/shirt/wrogn.jpg" />
        </div>
        """,
        "expected_price": 519.0,
        "expected_mrp": 2599.0,
        "expected_discount": 80.0,
    },
    # 12. Bank Offer Section (Ensure bank discount ₹200 is not price)
    {
        "url": "https://www.myntra.com/handbags/mango/mango-crossbody-bag/1213145/buy",
        "html": """
        <div class="pdp-details">
            <h1 class="pdp-title">MANGO</h1>
            <h1 class="pdp-name">Quilted Crossbody Bag</h1>
            <span class="pdp-price">₹2,990</span>
            <span class="pdp-mrp">₹4,590</span>
            <div class="pdp-offers">
                <span>10% Instant Discount on SBI Credit Cards</span>
            </div>
            <img class="image-grid-image" src="https://assets.myntassets.com/bag/mango.jpg" />
        </div>
        """,
        "expected_price": 2990.0,
        "expected_mrp": 4590.0,
        "expected_discount": 35.0,
    },
    # 13. Coupon Section (Ensure coupon discount ₹150 is rejected)
    {
        "url": "https://www.myntra.com/trousers/marks-spencer/formal-trousers/1314156/buy",
        "html": """
        <div class="pdp-details">
            <h1 class="pdp-title">Marks & Spencer</h1>
            <h1 class="pdp-name">Regular Fit Flat Front Trousers</h1>
            <span class="pdp-price">₹1,999</span>
            <span class="pdp-mrp">₹2,999</span>
            <div class="pdp-coupon">
                <span>Apply coupon MYNTRA200 for ₹200 off</span>
            </div>
            <img class="image-grid-image" src="https://assets.myntassets.com/ms/trouser.jpg" />
        </div>
        """,
        "expected_price": 1999.0,
        "expected_mrp": 2999.0,
        "expected_discount": 33.0,
    },
    # 14. Out of Stock Product
    {
        "url": "https://www.myntra.com/shoes/nike/nike-air-force-1/1415167/buy",
        "html": """
        <div class="pdp-details">
            <h1 class="pdp-title">Nike</h1>
            <h1 class="pdp-name">Air Force 1 '07 Sneakers</h1>
            <span class="pdp-price">₹8,195</span>
            <div class="pdp-out-of-stock">Item is currently out of stock.</div>
            <img class="image-grid-image" src="https://assets.myntassets.com/nike/af1.jpg" />
        </div>
        """,
        "expected_price": 8195.0,
        "expected_availability": AvailabilityEnum.out_of_stock,
    },
    # 15. Product with JSON-LD
    {
        "url": "https://www.myntra.com/heels/dressberry/block-heels/1516178/buy",
        "html": """
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "DressBerry Women Block Heels",
            "image": "https://assets.myntassets.com/heels/db.jpg",
            "offers": {
                "@type": "Offer",
                "price": "799",
                "highPrice": "1999",
                "priceCurrency": "INR"
            },
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": "4.2",
                "ratingCount": "3400"
            }
        }
        </script>
        <div class="pdp-details">
            <h1 class="pdp-name">DressBerry Block Heels</h1>
            <span class="pdp-price">₹799</span>
        </div>
        """,
        "expected_price": 799.0,
        "expected_mrp": 1999.0,
        "expected_discount": 60.0,
        "expected_rating": 4.2,
        "expected_rating_count": 3400,
    },
    # 16. Ratings in Lakhs
    {
        "url": "https://www.myntra.com/socks/puma/socks-pack-of-3/1617189/buy",
        "html": """
        <div class="pdp-details">
            <h1 class="pdp-title">Puma</h1>
            <h1 class="pdp-name">Unisex Pack of 3 Ankle Socks</h1>
            <span class="pdp-price">₹349</span>
            <span class="pdp-mrp">₹699</span>
            <div class="index-overallRating"><div>4.4</div></div>
            <div class="index-ratingsCount">1.2 lakh Ratings</div>
            <img class="image-grid-image" src="https://assets.myntassets.com/socks/puma.jpg" />
        </div>
        """,
        "expected_price": 349.0,
        "expected_mrp": 699.0,
        "expected_discount": 50.0,
        "expected_rating": 4.4,
        "expected_rating_count": 120000,
    },
    # 17. Brand + Title combination
    {
        "url": "https://www.myntra.com/wallets/tommy-hilfiger/leather-wallet/1718190/buy",
        "html": """
        <div class="pdp-details">
            <h1 class="pdp-title">Tommy Hilfiger</h1>
            <h1 class="pdp-name">Men Genuine Leather Two-Fold Wallet</h1>
            <span class="pdp-price">₹1,899</span>
            <span class="pdp-mrp">₹2,999</span>
            <img class="image-grid-image" src="https://assets.myntassets.com/wallet/th.jpg" />
        </div>
        """,
        "expected_price": 1899.0,
        "expected_mrp": 2999.0,
        "expected_discount": 37.0,
    },
    # 18. High-resolution image CDN URL
    {
        "url": "https://www.myntra.com/caps/adidas/baseball-cap/1819201/buy",
        "html": """
        <div class="pdp-details">
            <h1 class="pdp-title">Adidas</h1>
            <h1 class="pdp-name">Unisex Black Cotton Baseball Cap</h1>
            <span class="pdp-price">₹699</span>
            <span class="pdp-mrp">₹999</span>
            <img class="image-grid-image" src="https://assets.myntassets.com/h_1440,q_100,w_1080/adidas/cap.jpg" />
        </div>
        """,
        "expected_price": 699.0,
        "expected_mrp": 999.0,
        "expected_discount": 30.0,
    },
    # 19. Product without MRP (current price = MRP)
    {
        "url": "https://www.myntra.com/accessories/handcrafted/bracelet/1920212/buy",
        "html": """
        <div class="pdp-details">
            <h1 class="pdp-name">Handmade Beaded Charm Bracelet</h1>
            <span class="pdp-price">₹250</span>
            <img class="image-grid-image" src="https://assets.myntassets.com/bracelet.jpg" />
        </div>
        """,
        "expected_price": 250.0,
        "expected_mrp": None,
        "expected_discount": None,
    },
    # 20. Low Stock Alert
    {
        "url": "https://www.myntra.com/hoodies/levis/printed-hoodie/2021223/buy",
        "html": """
        <div class="pdp-details">
            <h1 class="pdp-title">LEVIS</h1>
            <h1 class="pdp-name">Men Graphic Print Fleece Hoodie</h1>
            <span class="pdp-price">₹1,799</span>
            <span class="pdp-mrp">₹3,599</span>
            <div class="low-inventory">Only 2 left in stock!</div>
            <img class="image-grid-image" src="https://assets.myntassets.com/hoodie/levis.jpg" />
        </div>
        """,
        "expected_price": 1799.0,
        "expected_mrp": 3599.0,
        "expected_discount": 50.0,
        "expected_availability": AvailabilityEnum.low_stock,
    },
]


@pytest.mark.parametrize("scenario", MYNTRA_SCENARIOS)
def test_myntra_20_scenarios(myntra_scraper, scenario):
    res = myntra_scraper.extract_from_html(scenario["html"], scenario["url"])
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
