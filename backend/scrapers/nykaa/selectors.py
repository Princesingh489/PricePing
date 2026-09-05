"""
Nykaa Selectors
"""
MAIN_CONTAINER_SELECTORS = [
    "div.product-details",
    "div.css-11v5k9",
    "div.css-1e5x64",
    "div.product-des-container",
]

TITLE_SELECTORS = [
    "h1.css-1gc4x7i",
    "h1.product-title",
    "h1.css-172z2in",
]

PRICE_SELECTORS = [
    "span.css-1jczs19",
    "span.css-11333m5",
    "span.post-discount",
]

MRP_SELECTORS = [
    "span.css-u05rr",
    "span.css-17x46k0",
    "span.pre-discount",
]

DISCOUNT_SELECTORS = [
    "span.css-14ns90f",
    "span.css-c69eb9",
]

IMAGE_SELECTORS = [
    "img[src*='/media/catalog/product/']",
    "div.main-product-image img",
    "div.css-1481bcp img",
    "div.css-1f6y8y8 img",
    "img.css-11gn9r6",
    "img.css-11v5k9",
    "div[class*='product-image'] img",
]

RATING_SELECTORS = [
    "div.css-15pe18n",
    "span.css-15pe18n",
]

COUNT_SELECTORS = [
    "span.css-1n9y6j",
    "span.css-1r0r6u9",
]

BRAND_SELECTORS = [
    "div.brand-name",
]

# Variant & Buybox Selectors
ACTIVE_SHADE_SELECTORS = [
    "div.shade-selector.selected",
    "div.css-1h99h1l.active",
    "span.shade-title",
]

BUYBOX_CART_BUTTONS = [
    "button.css-1r0r6u9",
    "button.css-1n9y6j",
    "button[aria-label*='Add to Bag']",
    "button.add-to-bag",
]

BUYBOX_OUT_OF_STOCK_SELECTORS = [
    "div.out-of-stock",
    "button[disabled].add-to-bag",
]
