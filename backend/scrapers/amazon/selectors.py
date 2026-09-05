"""
Amazon Selectors
"""
MAIN_CONTAINER_SELECTORS = [
    "#dp-container",
    "#ppd",
    "#centerCol",
    "#desktop_buybox",
]

TITLE_SELECTORS = [
    "h1#productTitle",
    "#productTitle",
    "span#productTitle",
    "h1.product-title",
    "#title",
]

PRICE_SELECTORS = [
    "#corePriceDisplay_desktop_feature_div span.a-price:not(.a-text-price) span.a-offscreen",
    "#corePriceDisplay_desktop_feature_div span.a-price-whole",
    "#corePrice_feature_div span.a-price:not(.a-text-price) span.a-offscreen",
    "#apex_desktop span.a-price:not(.a-text-price) span.a-offscreen",
    "#priceblock_ourprice",
    "#priceblock_dealprice",
    "span.a-price:not(.a-text-price) span.a-offscreen",
    "span.a-price:not(.a-text-price) span.a-price-whole",
]

MRP_SELECTORS = [
    "span.a-price.a-text-price span.a-offscreen",
    "#corePrice_feature_div span.a-price.a-text-price",
    "span.basisPrice span.a-offscreen",
]

DISCOUNT_SELECTORS = [
    "span.savingsPercentage",
    "span.reinventPriceSavingsPercentageMargin",
    "td.priceBlockSavingsString",
]

IMAGE_SELECTORS = [
    "img#landingImage",
    "img#imgBlkFront",
    "div#imgTagWrapperId img",
    "#main-image",
]

RATING_SELECTORS = [
    "#acrPopover span.a-icon-alt",
    "#acrPopover span.a-size-base",
    "i.a-icon-star span",
]

COUNT_SELECTORS = [
    "#acrCustomerReviewText",
    "#acrCustomerReviewLink",
]

BRAND_SELECTORS = [
    "#bylineInfo",
    "a#brand",
    "tr.po-brand td.po-break-word",
]

VARIANT_SELECTORS = [
    "#inline-twister-row-color_name .selection",
    "#inline-twister-row-size_name .selection",
    "#inline-twister-row-style_name .selection",
    "#variation_color_name .selection",
    "#variation_size_name .selection",
]

# Scoped Buybox Selectors
BUYBOX_CART_BUTTONS = [
    "#add-to-cart-button",
    "#buy-now-button",
    "#desktop_buybox input#add-to-cart-button",
    "#desktop_buybox input#buy-now-button",
]

BUYBOX_OUT_OF_STOCK_SELECTORS = [
    "#outOfStock",
    "#desktop_buybox div#outOfStock",
    "#availability span.a-color-price",
]
