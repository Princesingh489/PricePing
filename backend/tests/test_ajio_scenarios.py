import pytest
from scrapers.ajio_scraper import AjioScraper
from db.models import PlatformEnum, AvailabilityEnum


@pytest.fixture
def ajio_scraper():
    return AjioScraper()


AJIO_SCENARIOS = [
    # 1. Men Casual Shirt
    {
        "url": "https://www.ajio.com/netplay-men-checked-slim-fit-shirt/p/460123456_blue",
        "html": """
        <div class="prod-content">
            <h2 class="brand-name">NETPLAY</h2>
            <h1 class="prod-title">Men Checked Slim Fit Shirt</h1>
            <div class="prod-sp">₹499</div>
            <span class="prod-cp">₹1,299</span>
            <span class="prod-discnt">(62% off)</span>
            <div class="prod-rating">4.1</div>
            <div class="prod-rating-count">3,800 Ratings</div>
            <div class="img-holder"><img src="https://assets.ajio.com/medias/sys_master/root/460123_1.jpg" /></div>
        </div>
        """,
        "expected_price": 499.0,
        "expected_mrp": 1299.0,
        "expected_discount": 62.0,
        "expected_rating": 4.1,
        "expected_rating_count": 3800,
    },
    # 2. Women Kurta
    {
        "url": "https://www.ajio.com/avaasa-mix-n-match-printed-straight-kurta/p/461234567_pink",
        "html": """
        <div class="prod-content">
            <h2 class="brand-name">AVAASA MIX N' MATCH</h2>
            <h1 class="prod-title">Women Printed Straight Kurta</h1>
            <div class="prod-sp">₹399</div>
            <span class="prod-cp">₹799</span>
            <span class="prod-discnt">(50% off)</span>
            <div class="prod-rating">4.3</div>
            <div class="prod-rating-count">12,400 Ratings</div>
            <div class="img-holder"><img src="https://assets.ajio.com/avaasa.jpg" /></div>
        </div>
        """,
        "expected_price": 399.0,
        "expected_mrp": 799.0,
        "expected_discount": 50.0,
        "expected_rating": 4.3,
        "expected_rating_count": 12400,
    },
    # 3. Footwear - Sneakers
    {
        "url": "https://www.ajio.com/us-polo-assn-men-clarkin-sneakers/p/462345678_white",
        "html": """
        <div class="prod-content">
            <h2 class="brand-name">U.S. Polo Assn.</h2>
            <h1 class="prod-title">Men Clarkin Low-Top Lace-Up Sneakers</h1>
            <div class="prod-sp">₹1,799</div>
            <span class="prod-cp">₹3,599</span>
            <span class="prod-discnt">(50% off)</span>
            <div class="img-holder"><img src="https://assets.ajio.com/uspa.jpg" /></div>
        </div>
        """,
        "expected_price": 1799.0,
        "expected_mrp": 3599.0,
        "expected_discount": 50.0,
    },
    # 4. Handbag
    {
        "url": "https://www.ajio.com/caprese-women-structured-shoulder-bag/p/463456789_tan",
        "html": """
        <div class="prod-content">
            <h2 class="brand-name">Caprese</h2>
            <h1 class="prod-title">Women Textured Shoulder Bag</h1>
            <div class="prod-sp">₹1,599</div>
            <span class="prod-cp">₹3,999</span>
            <span class="prod-discnt">(60% off)</span>
            <div class="img-holder"><img src="https://assets.ajio.com/caprese.jpg" /></div>
        </div>
        """,
        "expected_price": 1599.0,
        "expected_mrp": 3999.0,
        "expected_discount": 60.0,
    },
    # 5. Trackpants
    {
        "url": "https://www.ajio.com/dnmx-men-slim-fit-track-pants/p/464567890_grey",
        "html": """
        <div class="prod-content">
            <h2 class="brand-name">DNMX</h2>
            <h1 class="prod-title">Men Slim Fit Track Pants with Insert Pockets</h1>
            <div class="prod-sp">₹449</div>
            <span class="prod-cp">₹899</span>
            <span class="prod-discnt">(50% off)</span>
            <div class="img-holder"><img src="https://assets.ajio.com/dnmx.jpg" /></div>
        </div>
        """,
        "expected_price": 449.0,
        "expected_mrp": 899.0,
        "expected_discount": 50.0,
    },
    # 6. Denim Jacket
    {
        "url": "https://www.ajio.com/lee-cooper-men-washed-denim-jacket/p/465678901_blue",
        "html": """
        <div class="prod-content">
            <h2 class="brand-name">Lee Cooper</h2>
            <h1 class="prod-title">Men Lightly Washed Denim Jacket</h1>
            <div class="prod-sp">₹1,999</div>
            <span class="prod-cp">₹4,999</span>
            <span class="prod-discnt">(60% off)</span>
            <div class="img-holder"><img src="https://assets.ajio.com/leecooper.jpg" /></div>
        </div>
        """,
        "expected_price": 1999.0,
        "expected_mrp": 4999.0,
        "expected_discount": 60.0,
    },
    # 7. T-Shirt
    {
        "url": "https://www.ajio.com/teamspirit-men-crew-neck-tshirt/p/466789012_black",
        "html": """
        <div class="prod-content">
            <h2 class="brand-name">Teamspirit</h2>
            <h1 class="prod-title">Men Crew-Neck Bio-Washed T-Shirt</h1>
            <div class="prod-sp">₹299</div>
            <span class="prod-cp">₹599</span>
            <span class="prod-discnt">(50% off)</span>
            <div class="img-holder"><img src="https://assets.ajio.com/teamspirit.jpg" /></div>
        </div>
        """,
        "expected_price": 299.0,
        "expected_mrp": 599.0,
        "expected_discount": 50.0,
    },
    # 8. Sweatshirt
    {
        "url": "https://www.ajio.com/gap-men-fleece-hooded-sweatshirt/p/467890123_navy",
        "html": """
        <div class="prod-content">
            <h2 class="brand-name">GAP</h2>
            <h1 class="prod-title">Men Logo Print Fleece Hoodie</h1>
            <div class="prod-sp">₹2,099</div>
            <span class="prod-cp">₹3,499</span>
            <span class="prod-discnt">(40% off)</span>
            <div class="img-holder"><img src="https://assets.ajio.com/gap.jpg" /></div>
        </div>
        """,
        "expected_price": 2099.0,
        "expected_mrp": 3499.0,
        "expected_discount": 40.0,
    },
    # 9. Belt / Wallet
    {
        "url": "https://www.ajio.com/wildhorn-leather-wallet-belt-gift-set/p/468901234_brown",
        "html": """
        <div class="prod-content">
            <h2 class="brand-name">Wildhorn</h2>
            <h1 class="prod-title">Men Leather Wallet & Reversible Belt Combo</h1>
            <div class="prod-sp">₹899</div>
            <span class="prod-cp">₹2,499</span>
            <span class="prod-discnt">(64% off)</span>
            <div class="img-holder"><img src="https://assets.ajio.com/wildhorn.jpg" /></div>
        </div>
        """,
        "expected_price": 899.0,
        "expected_mrp": 2499.0,
        "expected_discount": 64.0,
    },
    # 10. Ethnic Saree
    {
        "url": "https://www.ajio.com/indie-picks-pochampally-cotton-saree/p/469012345_yellow",
        "html": """
        <div class="prod-content">
            <h2 class="brand-name">Indie Picks</h2>
            <h1 class="prod-title">Handloom Pochampally Ikat Pure Cotton Saree</h1>
            <div class="prod-sp">₹1,249</div>
            <span class="prod-cp">₹2,499</span>
            <span class="prod-discnt">(50% off)</span>
            <div class="img-holder"><img src="https://assets.ajio.com/saree.jpg" /></div>
        </div>
        """,
        "expected_price": 1249.0,
        "expected_mrp": 2499.0,
        "expected_discount": 50.0,
    },
    # 11. Large Discount (75% off)
    {
        "url": "https://www.ajio.com/performax-men-quick-dry-shorts/p/470123456_blue",
        "html": """
        <div class="prod-content">
            <h2 class="brand-name">PERFORMAX</h2>
            <h1 class="prod-title">Men FastDry Training Shorts</h1>
            <div class="prod-sp">₹249</div>
            <span class="prod-cp">₹999</span>
            <span class="prod-discnt">(75% off)</span>
            <div class="img-holder"><img src="https://assets.ajio.com/performax.jpg" /></div>
        </div>
        """,
        "expected_price": 249.0,
        "expected_mrp": 999.0,
        "expected_discount": 75.0,
    },
    # 12. AJIOMANIA / Coupon Offer (Ensure coupon ₹250 is rejected)
    {
        "url": "https://www.ajio.com/crocs-bayaband-clogs/p/471234567_navy",
        "html": """
        <div class="prod-content">
            <h2 class="brand-name">Crocs</h2>
            <h1 class="prod-title">Unisex Bayaband Slip-On Clogs</h1>
            <div class="prod-sp">₹2,495</div>
            <span class="prod-cp">₹3,995</span>
            <div class="promo-discount">
                <span>Use code EPIC: Extra ₹400 Off on ₹2990</span>
            </div>
            <div class="img-holder"><img src="https://assets.ajio.com/crocs.jpg" /></div>
        </div>
        """,
        "expected_price": 2495.0,
        "expected_mrp": 3995.0,
        "expected_discount": 38.0,
    },
    # 13. Bank Discount section (Ensure 10% instant off is rejected)
    {
        "url": "https://www.ajio.com/red-tape-men-walking-shoes/p/472345678_black",
        "html": """
        <div class="prod-content">
            <h2 class="brand-name">Red Tape</h2>
            <h1 class="prod-title">Men Athleisure Memory Foam Shoes</h1>
            <div class="prod-sp">₹1,399</div>
            <span class="prod-cp">₹5,599</span>
            <div class="bank-offers">
                <span>Get 10% Instant Discount on Federal Bank Debit Cards</span>
            </div>
            <div class="img-holder"><img src="https://assets.ajio.com/redtape.jpg" /></div>
        </div>
        """,
        "expected_price": 1399.0,
        "expected_mrp": 5599.0,
        "expected_discount": 75.0,
    },
    # 14. Out of Stock item
    {
        "url": "https://www.ajio.com/superdry-men-vintage-logo-hoodie/p/473456789_orange",
        "html": """
        <div class="prod-content">
            <h2 class="brand-name">Superdry</h2>
            <h1 class="prod-title">Men Vintage Logo Embroidered Hoodie</h1>
            <div class="prod-sp">₹4,499</div>
            <div class="out-of-stock">Sold Out</div>
            <div class="img-holder"><img src="https://assets.ajio.com/superdry.jpg" /></div>
        </div>
        """,
        "expected_price": 4499.0,
        "expected_availability": AvailabilityEnum.out_of_stock,
    },
    # 15. Product with JSON-LD
    {
        "url": "https://www.ajio.com/mufti-men-textured-slim-fit-shirt/p/474567890_white",
        "html": """
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Mufti Men Textured Slim Fit Shirt",
            "image": "https://assets.ajio.com/mufti.jpg",
            "offers": {
                "@type": "Offer",
                "price": "1399",
                "highPrice": "2799",
                "priceCurrency": "INR"
            },
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": "4.2",
                "ratingCount": "1900"
            }
        }
        </script>
        <div class="prod-content">
            <h1 class="prod-title">Mufti Men Textured Slim Fit Shirt</h1>
            <div class="prod-sp">₹1,399</div>
        </div>
        """,
        "expected_price": 1399.0,
        "expected_mrp": 2799.0,
        "expected_discount": 50.0,
        "expected_rating": 4.2,
        "expected_rating_count": 1900,
    },
    # 16. Ratings & counts in Lakhs
    {
        "url": "https://www.ajio.com/jockey-men-cotton-boxer-briefs/p/475678901_navy",
        "html": """
        <div class="prod-content">
            <h2 class="brand-name">Jockey</h2>
            <h1 class="prod-title">Men Super Combed Cotton Boxer Briefs</h1>
            <div class="prod-sp">₹329</div>
            <span class="prod-cp">₹329</span>
            <div class="prod-rating">4.6</div>
            <div class="prod-rating-count">1.5 lakh Ratings</div>
            <div class="img-holder"><img src="https://assets.ajio.com/jockey.jpg" /></div>
        </div>
        """,
        "expected_price": 329.0,
        "expected_mrp": 329.0,
        "expected_rating": 4.6,
        "expected_rating_count": 150000,
    },
    # 17. Brand + Title combination
    {
        "url": "https://www.ajio.com/levis-men-511-slim-fit-jeans/p/476789012_blue",
        "html": """
        <div class="prod-content">
            <h2 class="brand-name">LEVI'S</h2>
            <h1 class="prod-title">511 Slim Fit Low Rise Jeans</h1>
            <div class="prod-sp">₹2,199</div>
            <span class="prod-cp">₹3,999</span>
            <div class="img-holder"><img src="https://assets.ajio.com/levis511.jpg" /></div>
        </div>
        """,
        "expected_price": 2199.0,
        "expected_mrp": 3999.0,
        "expected_discount": 45.0,
    },
    # 18. High-resolution gallery preview
    {
        "url": "https://www.ajio.com/van-heusen-men-formal-trousers/p/477890123_grey",
        "html": """
        <div class="prod-content">
            <h2 class="brand-name">Van Heusen</h2>
            <h1 class="prod-title">Men Slim Fit Formal Trousers</h1>
            <div class="prod-sp">₹1,299</div>
            <span class="prod-cp">₹2,199</span>
            <div class="img-holder"><img src="https://assets.ajio.com/vh.jpg" /></div>
        </div>
        """,
        "expected_price": 1299.0,
        "expected_mrp": 2199.0,
        "expected_discount": 41.0,
    },
    # 19. Product without MRP (current price = MRP)
    {
        "url": "https://www.ajio.com/artisan-brass-earrings/p/478901234_gold",
        "html": """
        <div class="prod-content">
            <h1 class="prod-title">Handcrafted Brass Jhumka Earrings</h1>
            <div class="prod-sp">₹450</div>
            <div class="img-holder"><img src="https://assets.ajio.com/jhumka.jpg" /></div>
        </div>
        """,
        "expected_price": 450.0,
        "expected_mrp": None,
        "expected_discount": None,
    },
    # 20. Low stock product
    {
        "url": "https://www.ajio.com/puma-men-racerback-tank-top/p/479012345_black",
        "html": """
        <div class="prod-content">
            <h2 class="brand-name">PUMA</h2>
            <h1 class="prod-title">Men Solid Training Tank Top</h1>
            <div class="prod-sp">₹649</div>
            <span class="prod-cp">₹1,299</span>
            <div class="stock-status">Only 1 left in stock</div>
            <div class="img-holder"><img src="https://assets.ajio.com/puma_tank.jpg" /></div>
        </div>
        """,
        "expected_price": 649.0,
        "expected_mrp": 1299.0,
        "expected_discount": 50.0,
        "expected_availability": AvailabilityEnum.low_stock,
    },
]


@pytest.mark.parametrize("scenario", AJIO_SCENARIOS)
def test_ajio_20_scenarios(ajio_scraper, scenario):
    res = ajio_scraper.extract_from_html(scenario["html"], scenario["url"])
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
