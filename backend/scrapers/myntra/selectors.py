"""
Myntra Selectors
"""
MAIN_CONTAINER_SELECTORS = [
    "div.pdp-details",
    "div.pdp-description-container",
    "div.pdp-container",
]

TITLE_SELECTORS = [
    "h1.pdp-name",
    "h1.pdp-title",
    "h1.title",
]

PRICE_SELECTORS = [
    "span.pdp-price",
    "span.pdp-offers-price",
    "div.pdp-price",
]

MRP_SELECTORS = [
    "span.pdp-mrp",
    "span.pdp-mrp-price",
]

DISCOUNT_SELECTORS = [
    "span.pdp-discount",
]

IMAGE_SELECTORS = [
    "img.image-grid-image",
    "div.image-grid-container img",
    "div.image-grid-imageContainer img",
    "img.pdp-image",
    "div[class*='image-grid'] img",
    "div[class*='slider-image'] img",
]

RATING_SELECTORS = [
    "div.index-overallRating div",
    "div.index-overallRating",
]

COUNT_SELECTORS = [
    "div.index-ratingsCount",
]

BRAND_SELECTORS = [
    "h1.pdp-title",
]

# Variant & Buybox Selectors
ACTIVE_SIZE_SELECTORS = [
    "button.size-buttons-size-button-selected",
    "button.size-buttons-size-button.active",
    "button.size-buttons-size-button",
]

BUYBOX_CART_BUTTONS = [
    "div.pdp-add-to-bag",
    "div.pdp-action-container .pdp-add-to-bag",
    "button.pdp-add-to-bag",
]

BUYBOX_OUT_OF_STOCK_SELECTORS = [
    "div.pdp-out-of-stock",
    "span.pdp-out-of-stock",
]
