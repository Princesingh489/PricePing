import pytest
from scrapers.flipkart_scraper import FlipkartScraper
from db.models import PlatformEnum, AvailabilityEnum


@pytest.fixture
def flipkart_scraper():
    return FlipkartScraper()


FLIPKART_SCENARIOS = [
    # 1. Smartphone
    {
        "url": "https://www.flipkart.com/poco-m6-pro-5g-power-black-128-gb/p/itm4c431dfc95786",
        "html": """
        <div class="DOjaWF">
            <span class="VU-ZEz">POCO M6 Pro 5G (Power Black, 128 GB)</span>
            <div class="Nx9bqj CxhGGd">₹9,999</div>
            <div class="yRaY8j">₹15,999</div>
            <div class="UkUFwK"><span>37% off</span></div>
            <img class="DByuf4" src="https://rukminim2.flixcart.com/image/128/128/xif0q/mobile/d/h/q/m6-pro-5g-mzb0epnin-poco-original-imags3e7vewsafg2.jpeg?q=70" />
            <div class="XQDdHH">4.3 ★</div>
            <span class="WNMewY"><span>1,24,560 Ratings & 8,920 Reviews</span></span>
        </div>
        """,
        "expected_price": 9999.0,
        "expected_mrp": 15999.0,
        "expected_discount": 37.0,
        "expected_rating": 4.3,
        "expected_rating_count": 124560,
        "expected_review_count": 8920,
    },
    # 2. Audio - Mivi Play Bluetooth Speaker
    {
        "url": "https://www.flipkart.com/mivi-play-12hrs-playback-bass-boosted-tws-feature-ipx4-5-w-portable-bluetooth-speaker/p/itm9e3dafa926a8d",
        "html": """
        <div class="DOjaWF">
            <span class="VU-ZEz">Mivi Play 12HRS Playback, Bass Boosted, TWS Feature, IPX4 5 W Portable Bluetooth Speaker</span>
            <div class="Nx9bqj CxhGGd">₹899</div>
            <div class="yRaY8j">₹1,999</div>
            <div class="UkUFwK"><span>55% off</span></div>
            <img class="DByuf4" src="https://rukminim2.flixcart.com/image/128/128/xif0q/speaker/blue_mivi.jpeg?q=70" />
            <div class="XQDdHH">4.2 ★</div>
            <span class="WNMewY"><span>1,48,271 Ratings & 12,450 Reviews</span></span>
        </div>
        """,
        "expected_price": 899.0,
        "expected_mrp": 1999.0,
        "expected_discount": 55.0,
        "expected_rating": 4.2,
        "expected_rating_count": 148271,
        "expected_review_count": 12450,
    },
    # 3. Smart TV
    {
        "url": "https://www.flipkart.com/mi-x-series-138-cm-55-inch-ultra-hd-4k-smart-google-tv/p/itm12345",
        "html": """
        <div class="DOjaWF">
            <span class="VU-ZEz">Mi X Series 138 cm (55 inch) Ultra HD (4K) Smart Google TV</span>
            <div class="Nx9bqj CxhGGd">₹36,999</div>
            <div class="yRaY8j">₹54,999</div>
            <div class="UkUFwK"><span>32% off</span></div>
            <img class="DByuf4" src="https://rukminim2.flixcart.com/image/128/128/tv.jpeg" />
            <div class="XQDdHH">4.4 ★</div>
            <span class="WNMewY"><span>14,500 Ratings & 1,200 Reviews</span></span>
        </div>
        """,
        "expected_price": 36999.0,
        "expected_mrp": 54999.0,
        "expected_discount": 32.0,
        "expected_rating": 4.4,
        "expected_rating_count": 14500,
    },
    # 4. Fashion - Men Jeans
    {
        "url": "https://www.flipkart.com/levi-s-men-slim-mid-rise-blue-jeans/p/itm556677",
        "html": """
        <div class="DOjaWF">
            <span class="VU-ZEz">LEVI'S Men Slim Mid Rise Blue Jeans</span>
            <div class="Nx9bqj CxhGGd">₹1,439</div>
            <div class="yRaY8j">₹3,199</div>
            <div class="UkUFwK"><span>55% off</span></div>
            <img class="DByuf4" src="https://rukminim2.flixcart.com/image/128/128/jeans.jpeg" />
            <div class="XQDdHH">4.1 ★</div>
            <span class="WNMewY"><span>4,200 Ratings & 350 Reviews</span></span>
        </div>
        """,
        "expected_price": 1439.0,
        "expected_mrp": 3199.0,
        "expected_discount": 55.0,
        "expected_rating": 4.1,
        "expected_rating_count": 4200,
    },
    # 5. Fashion - Women Saree
    {
        "url": "https://www.flipkart.com/kanjivaram-jacquard-silk-blend-saree/p/itm889900",
        "html": """
        <div class="DOjaWF">
            <span class="VU-ZEz">Kanjivaram Jacquard, Woven Silk Blend Saree</span>
            <div class="Nx9bqj CxhGGd">₹499</div>
            <div class="yRaY8j">₹2,999</div>
            <div class="UkUFwK"><span>83% off</span></div>
            <img class="DByuf4" src="https://rukminim2.flixcart.com/image/128/128/saree.jpeg" />
            <div class="XQDdHH">4.0 ★</div>
            <span class="WNMewY"><span>8,900 Ratings</span></span>
        </div>
        """,
        "expected_price": 499.0,
        "expected_mrp": 2999.0,
        "expected_discount": 83.0,
        "expected_rating": 4.0,
        "expected_rating_count": 8900,
    },
    # 6. Footwear - Sneakers
    {
        "url": "https://www.flipkart.com/asian-casual-sneaker-shoes/p/itm223344",
        "html": """
        <div class="DOjaWF">
            <span class="VU-ZEz">Asian Men White Casual Sneaker Shoes</span>
            <div class="Nx9bqj CxhGGd">₹699</div>
            <div class="yRaY8j">₹1,999</div>
            <div class="UkUFwK"><span>65% off</span></div>
            <img class="DByuf4" src="https://rukminim2.flixcart.com/image/128/128/shoes.jpeg" />
            <div class="XQDdHH">4.1 ★</div>
            <span class="WNMewY"><span>35,000 Ratings</span></span>
        </div>
        """,
        "expected_price": 699.0,
        "expected_mrp": 1999.0,
        "expected_discount": 65.0,
        "expected_rating": 4.1,
        "expected_rating_count": 35000,
    },
    # 7. Laptop
    {
        "url": "https://www.flipkart.com/acer-aspire-7-core-i5-12th-gen/p/itmlap77",
        "html": """
        <div class="DOjaWF">
            <span class="VU-ZEz">Acer Aspire 7 Intel Core i5 12th Gen Gaming Laptop</span>
            <div class="Nx9bqj CxhGGd">₹52,990</div>
            <div class="yRaY8j">₹82,999</div>
            <div class="UkUFwK"><span>36% off</span></div>
            <img class="DByuf4" src="https://rukminim2.flixcart.com/image/128/128/lap.jpeg" />
            <div class="XQDdHH">4.4 ★</div>
            <span class="WNMewY"><span>11,200 Ratings</span></span>
        </div>
        """,
        "expected_price": 52990.0,
        "expected_mrp": 82999.0,
        "expected_discount": 36.0,
        "expected_rating": 4.4,
        "expected_rating_count": 11200,
    },
    # 8. Washing Machine
    {
        "url": "https://www.flipkart.com/samsung-7-kg-5-star-fully-automatic-top-load/p/itmwash7",
        "html": """
        <div class="DOjaWF">
            <span class="VU-ZEz">Samsung 7 kg 5 Star Fully Automatic Top Load Washing Machine</span>
            <div class="Nx9bqj CxhGGd">₹15,490</div>
            <div class="yRaY8j">₹21,000</div>
            <div class="UkUFwK"><span>26% off</span></div>
            <img class="DByuf4" src="https://rukminim2.flixcart.com/image/128/128/wm.jpeg" />
            <div class="XQDdHH">4.5 ★</div>
            <span class="WNMewY"><span>48,900 Ratings</span></span>
        </div>
        """,
        "expected_price": 15490.0,
        "expected_mrp": 21000.0,
        "expected_discount": 26.0,
        "expected_rating": 4.5,
        "expected_rating_count": 48900,
    },
    # 9. Beauty - Face Wash
    {
        "url": "https://www.flipkart.com/himalaya-purifying-neem-face-wash-300-ml/p/itmface9",
        "html": """
        <div class="DOjaWF">
            <span class="VU-ZEz">Himalaya Purifying Neem Face Wash (300 ml)</span>
            <div class="Nx9bqj CxhGGd">₹269</div>
            <div class="yRaY8j">₹350</div>
            <div class="UkUFwK"><span>23% off</span></div>
            <img class="DByuf4" src="https://rukminim2.flixcart.com/image/128/128/facewash.jpeg" />
            <div class="XQDdHH">4.5 ★</div>
            <span class="WNMewY"><span>95,000 Ratings</span></span>
        </div>
        """,
        "expected_price": 269.0,
        "expected_mrp": 350.0,
        "expected_discount": 23.0,
        "expected_rating": 4.5,
        "expected_rating_count": 95000,
    },
    # 10. Tablet
    {
        "url": "https://www.flipkart.com/lenovo-tab-m10-fhd-plus-4-gb-ram-128-gb/p/itmtab10",
        "html": """
        <div class="DOjaWF">
            <span class="VU-ZEz">Lenovo Tab M10 FHD Plus (4 GB RAM, 128 GB ROM)</span>
            <div class="Nx9bqj CxhGGd">₹12,999</div>
            <div class="yRaY8j">₹28,000</div>
            <div class="UkUFwK"><span>53% off</span></div>
            <img class="DByuf4" src="https://rukminim2.flixcart.com/image/128/128/tab.jpeg" />
            <div class="XQDdHH">4.2 ★</div>
            <span class="WNMewY"><span>18,200 Ratings</span></span>
        </div>
        """,
        "expected_price": 12999.0,
        "expected_mrp": 28000.0,
        "expected_discount": 53.0,
        "expected_rating": 4.2,
        "expected_rating_count": 18200,
    },
    # 11. Large Discount Clearance item
    {
        "url": "https://www.flipkart.com/clever-cutter-stainless-steel-knife/p/itmclear",
        "html": """
        <div class="DOjaWF">
            <span class="VU-ZEz">2-in-1 Knife and Cutting Board</span>
            <div class="Nx9bqj CxhGGd">₹99</div>
            <div class="yRaY8j">₹699</div>
            <div class="UkUFwK"><span>85% off</span></div>
            <img class="DByuf4" src="https://rukminim2.flixcart.com/image/128/128/knife.jpeg" />
        </div>
        """,
        "expected_price": 99.0,
        "expected_mrp": 699.0,
        "expected_discount": 85.0,
    },
    # 12. Bank Offer section (Ensure bank discount ₹1,000 is not price)
    {
        "url": "https://www.flipkart.com/motorola-g34-5g-charcoal-black-128-gb/p/itmg34",
        "html": """
        <div class="DOjaWF">
            <span class="VU-ZEz">Motorola G34 5G (Charcoal Black, 128 GB)</span>
            <div class="Nx9bqj CxhGGd">₹11,999</div>
            <div class="yRaY8j">₹14,999</div>
            <div class="offers-wrapper">
                <span>Bank Offer: ₹1,000 Off on Axis Bank Credit Cards</span>
            </div>
            <img class="DByuf4" src="https://rukminim2.flixcart.com/image/128/128/moto.jpeg" />
        </div>
        """,
        "expected_price": 11999.0,
        "expected_mrp": 14999.0,
        "expected_discount": 20.0,
    },
    # 13. SuperCoins / Cashback Offer (Ensure ₹50 cashback is rejected)
    {
        "url": "https://www.flipkart.com/boat-airdopes-131-bluetooth-headset/p/itmboat",
        "html": """
        <div class="DOjaWF">
            <span class="VU-ZEz">boAt Airdopes 131 with 60 Hours Playback</span>
            <div class="Nx9bqj CxhGGd">₹899</div>
            <div class="yRaY8j">₹2,990</div>
            <div class="special-offer">
                <span>Save extra ₹50 using 50 SuperCoins</span>
            </div>
            <img class="DByuf4" src="https://rukminim2.flixcart.com/image/128/128/boat.jpeg" />
        </div>
        """,
        "expected_price": 899.0,
        "expected_mrp": 2990.0,
        "expected_discount": 70.0,
    },
    # 14. Exchange Offer section (Ensure ₹8,000 exchange is rejected)
    {
        "url": "https://www.flipkart.com/vivo-t3x-5g-crimson-bliss-128-gb/p/itmvivo",
        "html": """
        <div class="DOjaWF">
            <span class="VU-ZEz">vivo T3x 5G (Crimson Bliss, 128 GB)</span>
            <div class="Nx9bqj CxhGGd">₹13,499</div>
            <div class="yRaY8j">₹17,499</div>
            <div class="exchange-offer">
                <span>Buy with Exchange: Up to ₹11,000 off</span>
            </div>
            <img class="DByuf4" src="https://rukminim2.flixcart.com/image/128/128/vivo.jpeg" />
        </div>
        """,
        "expected_price": 13499.0,
        "expected_mrp": 17499.0,
        "expected_discount": 23.0,
    },
    # 15. EMI section (Ensure ₹460/mo is rejected)
    {
        "url": "https://www.flipkart.com/godrej-180-l-direct-cool-single-door-refrigerator/p/itmgodrej",
        "html": """
        <div class="DOjaWF">
            <span class="VU-ZEz">Godrej 180 L Direct Cool Single Door 2 Star Refrigerator</span>
            <div class="Nx9bqj CxhGGd">₹12,490</div>
            <div class="yRaY8j">₹16,500</div>
            <div class="emi-plans">
                <span>Standard EMI from ₹434/month</span>
            </div>
            <img class="DByuf4" src="https://rukminim2.flixcart.com/image/128/128/fridge.jpeg" />
        </div>
        """,
        "expected_price": 12490.0,
        "expected_mrp": 16500.0,
        "expected_discount": 24.0,
    },
    # 16. Product with JSON-LD
    {
        "url": "https://www.flipkart.com/noise-buds-vs102-true-wireless-earbuds/p/itmnoise",
        "html": """
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Noise Buds VS102 Truly Wireless Earbuds",
            "image": "https://rukminim2.flixcart.com/image/832/832/noise.jpg",
            "offers": {
                "@type": "Offer",
                "price": "999",
                "highPrice": "2999",
                "priceCurrency": "INR"
            },
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": "4.1",
                "ratingCount": "84000"
            }
        }
        </script>
        <div class="DOjaWF">
            <span class="VU-ZEz">Noise Buds VS102</span>
            <div class="Nx9bqj CxhGGd">₹999</div>
        </div>
        """,
        "expected_price": 999.0,
        "expected_mrp": 2999.0,
        "expected_discount": 67.0,
        "expected_rating": 4.1,
        "expected_rating_count": 84000,
    },
    # 17. Product with rating and review string in Lakhs
    {
        "url": "https://www.flipkart.com/sandisk-cruzer-blade-32-gb-pendrive/p/itmsandisk",
        "html": """
        <div class="DOjaWF">
            <span class="VU-ZEz">SanDisk Cruzer Blade 32 GB USB 2.0 Pen Drive</span>
            <div class="Nx9bqj CxhGGd">₹349</div>
            <div class="yRaY8j">₹650</div>
            <div class="XQDdHH">4.3 ★</div>
            <span class="WNMewY"><span>1.5 lakh Ratings & 12,000 Reviews</span></span>
            <img class="DByuf4" src="https://rukminim2.flixcart.com/image/128/128/pendrive.jpg" />
        </div>
        """,
        "expected_price": 349.0,
        "expected_mrp": 650.0,
        "expected_rating": 4.3,
        "expected_rating_count": 150000,
        "expected_review_count": 12000,
    },
    # 18. Out of Stock Product
    {
        "url": "https://www.flipkart.com/sony-playstation-5-console/p/itmps5",
        "html": """
        <div class="DOjaWF">
            <span class="VU-ZEz">SONY PlayStation 5 (PS5) 825 GB</span>
            <div class="Nx9bqj CxhGGd">₹44,990</div>
            <div class="_16FRp0">Sold Out. This item is currently unavailable.</div>
            <img class="DByuf4" src="https://rukminim2.flixcart.com/image/128/128/ps5.jpg" />
        </div>
        """,
        "expected_price": 44990.0,
        "expected_availability": AvailabilityEnum.out_of_stock,
    },
    # 19. High-res image with srcset
    {
        "url": "https://www.flipkart.com/fastrack-reflex-vox-smartwatch/p/itmfast",
        "html": """
        <div class="DOjaWF">
            <span class="VU-ZEz">Fastrack Reflex VOX 2.0 Smartwatch</span>
            <div class="Nx9bqj CxhGGd">₹1,995</div>
            <div class="yRaY8j">₹4,995</div>
            <img class="DByuf4" srcset="https://rukminim2.flixcart.com/image/128/128/watch.jpg 128w, https://rukminim2.flixcart.com/image/832/832/watch.jpg 832w" src="https://rukminim2.flixcart.com/image/128/128/watch.jpg" />
        </div>
        """,
        "expected_price": 1995.0,
        "expected_mrp": 4995.0,
        "expected_discount": 60.0,
    },
    # 20. Product without MRP
    {
        "url": "https://www.flipkart.com/artisan-clay-tea-cups-set-of-6/p/itmclay",
        "html": """
        <div class="DOjaWF">
            <span class="VU-ZEz">Handcrafted Clay Tea Cups (Set of 6)</span>
            <div class="Nx9bqj CxhGGd">₹350</div>
            <img class="DByuf4" src="https://rukminim2.flixcart.com/image/128/128/cups.jpg" />
        </div>
        """,
        "expected_price": 350.0,
        "expected_mrp": None,
        "expected_discount": None,
    },
]


@pytest.mark.parametrize("scenario", FLIPKART_SCENARIOS)
def test_flipkart_20_scenarios(flipkart_scraper, scenario):
    res = flipkart_scraper.extract_from_html(scenario["html"], scenario["url"])
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
    if "expected_review_count" in scenario:
        assert res.review_count == scenario["expected_review_count"]
    if "expected_availability" in scenario:
        assert res.availability == scenario["expected_availability"]
