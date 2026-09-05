"""
AJIO Selectors
==============
Selectors supporting desktop, mobile, and dynamic React DOM templates on AJIO.
"""
MAIN_CONTAINER_SELECTORS = [
    "div#appContainer",
    "div#app",
    "div.prod-content",
    "div.prod-container",
    "div.product-details",
    "div[class*='pdp-container']",
    "div[class*='product-information']",
]

TITLE_SELECTORS = [
    "h1.prod-title",
    "h1.prod-name",
    "h1.name",
    "h1[class*='title']",
    "h1[class*='name']",
    ".prod-title",
    ".prod-name",
    "h1",
]

PRICE_SELECTORS = [
    "div.prod-sp",
    "span.prod-sp",
    "span.price-value",
    "div[class*='prod-sp']",
    "span[class*='prod-sp']",
    "div[class*='price-wrapper'] span",
]

MRP_SELECTORS = [
    "span.prod-cp",
    "span.prod-mrp",
    "span[class*='prod-cp']",
    "span[class*='prod-mrp']",
    "div[class*='mrp']",
    "span[class*='mrp']",
]

DISCOUNT_SELECTORS = [
    "span.prod-discnt",
    "span[class*='prod-discnt']",
    "span[class*='discount']",
    "div[class*='discount']",
]

IMAGE_SELECTORS = [
    "div.img-holder img",
    "div.image-holder img",
    "img.preview-image",
    "div[class*='image-container'] img",
    "img[class*='rilrtl-lazy-img']",
    "div[class*='slick-active'] img",
]

RATING_SELECTORS = [
    "div.prod-rating",
    "span.prod-rating",
    "div[class*='rating']",
    "span[class*='rating']",
]

COUNT_SELECTORS = [
    "div.prod-rating-count",
    "span.prod-rating-count",
    "div[class*='rating-count']",
    "span[class*='rating-count']",
]

BRAND_SELECTORS = [
    "h2.brand-name",
    "h2[class*='brand']",
    "a[class*='brand']",
    "div[class*='brand-name']",
]

# Variant & Buybox Selectors
ACTIVE_SIZE_SELECTORS = [
    "div.size-variant-item.selected",
    "div.size-variant-item.active",
    "div.size-swatch.active",
    "div.size-swatch.selected",
    "div[class*='size-variant-item'][class*='active']",
    "div[class*='size-variant-item'][class*='selected']",
]

ACTIVE_COLOR_SELECTORS = [
    "div.color-swatch.selected",
    "div.color-swatch.active",
    "div[class*='color-swatch'][class*='active']",
    "div[class*='color-swatch'][class*='selected']",
]

BUYBOX_CART_BUTTONS = [
    "div.btn-gold",
    "div.pdp-add-to-bag",
    "button.btn-gold",
    "div.add-to-bag",
    "div[class*='add-to-bag']",
    "div[class*='btn-gold']",
    "button[class*='btn-gold']",
    "button[class*='add-to-bag']",
]

BUYBOX_OUT_OF_STOCK_SELECTORS = [
    "div.out-of-stock",
    "div.out-of-stock-banner",
    "div[class*='out-of-stock']",
    "span[class*='out-of-stock']",
    "div[class*='sold-out']",
    "span[class*='sold-out']",
]
