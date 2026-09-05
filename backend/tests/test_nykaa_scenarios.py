import pytest
from scrapers.nykaa_scraper import NykaaScraper
from db.models import PlatformEnum, AvailabilityEnum


@pytest.fixture
def nykaa_scraper():
    return NykaaScraper()


NYKAA_SCENARIOS = [
    # 1. Lipstick (Maybelline Matte Liquid Lipstick)
    {
        "url": "https://www.nykaa.com/maybelline-new-york-super-stay-matte-ink-liquid-lipstick/p/231234",
        "html": """
        <div class="product-details">
            <h1 class="css-1gc4x7i">Maybelline New York Super Stay Matte Ink Liquid Lipstick - Ruler</h1>
            <span class="css-1jczs19">₹559</span>
            <span class="css-u05rr">₹699</span>
            <span class="css-14ns90f">20% Off</span>
            <div class="css-15pe18n">4.4</div>
            <span class="css-1n9y6j">45,800 Ratings</span>
            <div class="main-product-image"><img src="https://images-static.nykaa.com/media/catalog/product/maybelline_ruler.jpg" /></div>
        </div>
        """,
        "expected_price": 559.0,
        "expected_mrp": 699.0,
        "expected_discount": 20.0,
        "expected_rating": 4.4,
        "expected_rating_count": 45800,
    },
    # 2. Skincare - Vitamin C Serum
    {
        "url": "https://www.nykaa.com/minimalist-10percent-vitamin-c-face-serum/p/123456",
        "html": """
        <div class="product-details">
            <h1 class="css-1gc4x7i">Minimalist 10% Vitamin C Face Serum For Glowing Skin</h1>
            <span class="css-1jczs19">₹664</span>
            <span class="css-u05rr">₹699</span>
            <span class="css-14ns90f">5% Off</span>
            <div class="css-15pe18n">4.5</div>
            <span class="css-1n9y6j">18,200 Ratings</span>
            <div class="main-product-image"><img src="https://images-static.nykaa.com/media/catalog/product/minimalist_vit_c.jpg" /></div>
        </div>
        """,
        "expected_price": 664.0,
        "expected_mrp": 699.0,
        "expected_discount": 5.0,
        "expected_rating": 4.5,
        "expected_rating_count": 18200,
    },
    # 3. Sunscreen - SPF 50
    {
        "url": "https://www.nykaa.com/aqualogica-glow-dewy-sunscreen-spf-50-pa/p/345678",
        "html": """
        <div class="product-details">
            <h1 class="css-1gc4x7i">Aqualogica Radiance+ Dewy Sunscreen with Papaya & Vitamin C - 50g</h1>
            <span class="css-1jczs19">₹399</span>
            <span class="css-u05rr">₹499</span>
            <span class="css-14ns90f">20% Off</span>
            <div class="css-15pe18n">4.3</div>
            <span class="css-1n9y6j">24,500 Ratings</span>
            <div class="main-product-image"><img src="https://images-static.nykaa.com/sunscreen.jpg" /></div>
        </div>
        """,
        "expected_price": 399.0,
        "expected_mrp": 499.0,
        "expected_discount": 20.0,
        "expected_rating": 4.3,
        "expected_rating_count": 24500,
    },
    # 4. Haircare - Hair Mask
    {
        "url": "https://www.nykaa.com/loreal-professionnel-absolut-repair-hair-mask/p/456789",
        "html": """
        <div class="product-details">
            <h1 class="css-1gc4x7i">L'Oreal Professionnel Serie Expert Absolut Repair Hair Mask - 250ml</h1>
            <span class="css-1jczs19">₹855</span>
            <span class="css-u05rr">₹950</span>
            <span class="css-14ns90f">10% Off</span>
            <div class="css-15pe18n">4.6</div>
            <span class="css-1n9y6j">12,100 Ratings</span>
            <div class="main-product-image"><img src="https://images-static.nykaa.com/loreal_mask.jpg" /></div>
        </div>
        """,
        "expected_price": 855.0,
        "expected_mrp": 950.0,
        "expected_discount": 10.0,
        "expected_rating": 4.6,
        "expected_rating_count": 12100,
    },
    # 5. Fragrance - Perfume EDP
    {
        "url": "https://www.nykaa.com/plum-bodylovin-vanilla-vibes-eau-de-parfum/p/567890",
        "html": """
        <div class="product-details">
            <h1 class="css-1gc4x7i">Plum BodyLovin' Vanilla Vibes Eau De Parfum - 50ml</h1>
            <span class="css-1jczs19">₹446</span>
            <span class="css-u05rr">₹595</span>
            <span class="css-14ns90f">25% Off</span>
            <div class="css-15pe18n">4.4</div>
            <span class="css-1n9y6j">8,900 Ratings</span>
            <div class="main-product-image"><img src="https://images-static.nykaa.com/plum_vanilla.jpg" /></div>
        </div>
        """,
        "expected_price": 446.0,
        "expected_mrp": 595.0,
        "expected_discount": 25.0,
        "expected_rating": 4.4,
        "expected_rating_count": 8900,
    },
    # 6. Makeup Foundation
    {
        "url": "https://www.nykaa.com/kay-beauty-hydrating-foundation/p/678901",
        "html": """
        <div class="product-details">
            <h1 class="css-1gc4x7i">Kay Beauty Hydrating Foundation - 120Y Light</h1>
            <span class="css-1jczs19">₹960</span>
            <span class="css-u05rr">₹1,200</span>
            <span class="css-14ns90f">20% Off</span>
            <div class="css-15pe18n">4.5</div>
            <span class="css-1n9y6j">15,600 Ratings</span>
            <div class="main-product-image"><img src="https://images-static.nykaa.com/kay_foundation.jpg" /></div>
        </div>
        """,
        "expected_price": 960.0,
        "expected_mrp": 1200.0,
        "expected_discount": 20.0,
        "expected_rating": 4.5,
        "expected_rating_count": 15600,
    },
    # 7. Eye Liner / Kajal
    {
        "url": "https://www.nykaa.com/lakme-eyeconic-kajal/p/789012",
        "html": """
        <div class="product-details">
            <h1 class="css-1gc4x7i">Lakme Eyeconic Kajal - Deep Black</h1>
            <span class="css-1jczs19">₹185</span>
            <span class="css-u05rr">₹250</span>
            <span class="css-14ns90f">26% Off</span>
            <div class="css-15pe18n">4.3</div>
            <span class="css-1n9y6j">85,000 Ratings</span>
            <div class="main-product-image"><img src="https://images-static.nykaa.com/lakme_kajal.jpg" /></div>
        </div>
        """,
        "expected_price": 185.0,
        "expected_mrp": 250.0,
        "expected_discount": 26.0,
        "expected_rating": 4.3,
        "expected_rating_count": 85000,
    },
    # 8. Face Moisturizer
    {
        "url": "https://www.nykaa.com/cetaphil-moisturising-cream/p/890123",
        "html": """
        <div class="product-details">
            <h1 class="css-1gc4x7i">Cetaphil Moisturising Cream For Dry To Normal, Sensitive Skin - 100g</h1>
            <span class="css-1jczs19">₹472</span>
            <span class="css-u05rr">₹555</span>
            <span class="css-14ns90f">15% Off</span>
            <div class="css-15pe18n">4.6</div>
            <span class="css-1n9y6j">54,000 Ratings</span>
            <div class="main-product-image"><img src="https://images-static.nykaa.com/cetaphil.jpg" /></div>
        </div>
        """,
        "expected_price": 472.0,
        "expected_mrp": 555.0,
        "expected_discount": 15.0,
        "expected_rating": 4.6,
        "expected_rating_count": 54000,
    },
    # 9. Bath & Body - Body Wash
    {
        "url": "https://www.nykaa.com/dove-deep-moisture-body-wash/p/901234",
        "html": """
        <div class="product-details">
            <h1 class="css-1gc4x7i">Dove Deeply Nourishing Body Wash - 800ml</h1>
            <span class="css-1jczs19">₹385</span>
            <span class="css-u05rr">₹550</span>
            <span class="css-14ns90f">30% Off</span>
            <div class="css-15pe18n">4.4</div>
            <span class="css-1n9y6j">22,000 Ratings</span>
            <div class="main-product-image"><img src="https://images-static.nykaa.com/dove_wash.jpg" /></div>
        </div>
        """,
        "expected_price": 385.0,
        "expected_mrp": 550.0,
        "expected_discount": 30.0,
        "expected_rating": 4.4,
        "expected_rating_count": 22000,
    },
    # 10. Luxury Beauty - Estee Lauder
    {
        "url": "https://www.nykaa.com/estee-lauder-advanced-night-repair-synchronized-multi-recovery-complex/p/101112",
        "html": """
        <div class="product-details">
            <h1 class="css-1gc4x7i">Estee Lauder Advanced Night Repair Synchronized Multi-Recovery Complex - 50ml</h1>
            <span class="css-1jczs19">₹8,900</span>
            <span class="css-u05rr">₹8,900</span>
            <div class="css-15pe18n">4.7</div>
            <span class="css-1n9y6j">6,200 Ratings</span>
            <div class="main-product-image"><img src="https://images-static.nykaa.com/anr.jpg" /></div>
        </div>
        """,
        "expected_price": 8900.0,
        "expected_mrp": 8900.0,
        "expected_rating": 4.7,
        "expected_rating_count": 6200,
    },
    # 11. Large Discount Clearance (65% off)
    {
        "url": "https://www.nykaa.com/nykaa-cosmetics-matte-to-last-metallic-liquid-lipstick/p/111213",
        "html": """
        <div class="product-details">
            <h1 class="css-1gc4x7i">Nykaa Cosmetics Matte to Last Metallic Liquid Lipstick</h1>
            <span class="css-1jczs19">₹210</span>
            <span class="css-u05rr">₹599</span>
            <span class="css-14ns90f">65% Off</span>
            <div class="main-product-image"><img src="https://images-static.nykaa.com/nykaa_metallic.jpg" /></div>
        </div>
        """,
        "expected_price": 210.0,
        "expected_mrp": 599.0,
        "expected_discount": 65.0,
    },
    # 12. Combo Offer / Free Gift (Ensure gift ₹0 / ₹199 is not selling price)
    {
        "url": "https://www.nykaa.com/biotique-bio-dandelion-visibly-ageless-serum/p/121314",
        "html": """
        <div class="product-details">
            <h1 class="css-1gc4x7i">Biotique Dandelion Visibly Ageless Serum - 40ml</h1>
            <span class="css-1jczs19">₹182</span>
            <span class="css-u05rr">₹260</span>
            <div class="free-gift-banner">
                <span>Free Biotique Lip Balm worth ₹175 on orders above ₹499</span>
            </div>
            <div class="main-product-image"><img src="https://images-static.nykaa.com/biotique.jpg" /></div>
        </div>
        """,
        "expected_price": 182.0,
        "expected_mrp": 260.0,
        "expected_discount": 30.0,
    },
    # 13. Bank Discount section (Ensure 10% instant off is rejected)
    {
        "url": "https://www.nykaa.com/clinique-moisture-surge-100h-auto-replenishing-hydrator/p/131415",
        "html": """
        <div class="product-details">
            <h1 class="css-1gc4x7i">Clinique Moisture Surge 100H Auto-Replenishing Hydrator - 50ml</h1>
            <span class="css-1jczs19">₹2,950</span>
            <span class="css-u05rr">₹2,950</span>
            <div class="bank-offers">
                <span>Get 10% off up to ₹500 on HDFC Bank Credit Cards</span>
            </div>
            <div class="main-product-image"><img src="https://images-static.nykaa.com/clinique.jpg" /></div>
        </div>
        """,
        "expected_price": 2950.0,
        "expected_mrp": 2950.0,
    },
    # 14. Out of Stock item
    {
        "url": "https://www.nykaa.com/rare-beauty-soft-pinch-liquid-blush-hope/p/141516",
        "html": """
        <div class="product-details">
            <h1 class="css-1gc4x7i">Rare Beauty Soft Pinch Liquid Blush - Hope</h1>
            <span class="css-1jczs19">₹2,900</span>
            <div class="stock-status">Out Of Stock</div>
            <div class="main-product-image"><img src="https://images-static.nykaa.com/rare_hope.jpg" /></div>
        </div>
        """,
        "expected_price": 2900.0,
        "expected_availability": AvailabilityEnum.out_of_stock,
    },
    # 15. Product with JSON-LD schema
    {
        "url": "https://www.nykaa.com/forest-essentials-facial-tonic-mist-pure-rosewater/p/151617",
        "html": """
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Forest Essentials Facial Tonic Mist Pure Rosewater - 200ml",
            "image": "https://images-static.nykaa.com/fe_rose.jpg",
            "offers": {
                "@type": "Offer",
                "price": "1450",
                "highPrice": "1450",
                "priceCurrency": "INR"
            },
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": "4.6",
                "ratingCount": "7800"
            }
        }
        </script>
        <div class="product-details">
            <h1 class="css-1gc4x7i">Forest Essentials Pure Rosewater</h1>
            <span class="css-1jczs19">₹1,450</span>
        </div>
        """,
        "expected_price": 1450.0,
        "expected_mrp": 1450.0,
        "expected_rating": 4.6,
        "expected_rating_count": 7800,
    },
    # 16. Ratings & reviews in Lakhs
    {
        "url": "https://www.nykaa.com/garnier-skin-naturals-micellar-cleansing-water/p/161718",
        "html": """
        <div class="product-details">
            <h1 class="css-1gc4x7i">Garnier Skin Naturals Micellar Cleansing Water - 400ml</h1>
            <span class="css-1jczs19">₹319</span>
            <span class="css-u05rr">₹399</span>
            <div class="css-15pe18n">4.5</div>
            <span class="css-1n9y6j">1.8 lakh Ratings</span>
            <div class="main-product-image"><img src="https://images-static.nykaa.com/garnier.jpg" /></div>
        </div>
        """,
        "expected_price": 319.0,
        "expected_mrp": 399.0,
        "expected_discount": 20.0,
        "expected_rating": 4.5,
        "expected_rating_count": 180000,
    },
    # 17. High-res product slider image
    {
        "url": "https://www.nykaa.com/maccosmetics-retro-matte-lipstick-ruby-woo/p/171819",
        "html": """
        <div class="product-details">
            <h1 class="css-1gc4x7i">M.A.C Retro Matte Lipstick - Ruby Woo</h1>
            <span class="css-1jczs19">₹1,950</span>
            <span class="css-u05rr">₹1,950</span>
            <div class="main-product-image"><img src="https://images-static.nykaa.com/media/catalog/product/ruby_woo_hires.jpg" /></div>
        </div>
        """,
        "expected_price": 1950.0,
        "expected_mrp": 1950.0,
    },
    # 18. Brand + Title combination
    {
        "url": "https://www.nykaa.com/the-ordinary-niacinamide-10percent-plus-zinc-1percent/p/181920",
        "html": """
        <div class="product-details">
            <h1 class="css-1gc4x7i">The Ordinary Niacinamide 10% + Zinc 1% - 30ml</h1>
            <span class="css-1jczs19">₹600</span>
            <div class="main-product-image"><img src="https://images-static.nykaa.com/ordinary_nia.jpg" /></div>
        </div>
        """,
        "expected_price": 600.0,
        "expected_mrp": None,
        "expected_discount": None,
    },
    # 19. Product without MRP (current price = MRP)
    {
        "url": "https://www.nykaa.com/organic-harvest-handmade-soap/p/192021",
        "html": """
        <div class="product-details">
            <h1 class="css-1gc4x7i">Organic Harvest Handmade Neem & Tulsi Bathing Bar</h1>
            <span class="css-1jczs19">₹99</span>
            <div class="main-product-image"><img src="https://images-static.nykaa.com/soap.jpg" /></div>
        </div>
        """,
        "expected_price": 99.0,
        "expected_mrp": None,
        "expected_discount": None,
    },
    # 20. Low stock product
    {
        "url": "https://www.nykaa.com/charlotte-tilbury-pillow-talk-matte-revolution/p/202122",
        "html": """
        <div class="product-details">
            <h1 class="css-1gc4x7i">Charlotte Tilbury Matte Revolution - Pillow Talk</h1>
            <span class="css-1jczs19">₹3,400</span>
            <div class="stock-info">Only 3 left in stock</div>
            <div class="main-product-image"><img src="https://images-static.nykaa.com/pillow_talk.jpg" /></div>
        </div>
        """,
        "expected_price": 3400.0,
        "expected_availability": AvailabilityEnum.low_stock,
    },
]


@pytest.mark.parametrize("scenario", NYKAA_SCENARIOS)
def test_nykaa_20_scenarios(nykaa_scraper, scenario):
    res = nykaa_scraper.extract_from_html(scenario["html"], scenario["url"])
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
