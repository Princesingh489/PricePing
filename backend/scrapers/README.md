# 🕷️ PriceWatch Scraping Subsystem Documentation

Welcome to the **PriceWatch Scrapers Module** (`backend/scrapers`). This directory contains the modular, store-specific web scraping engine designed to reliably extract product details (titles, real-time selling prices, MRP/original prices, discount percentages, high-resolution product images, and stock availability) across major Indian e-commerce platforms.

---

## 📑 Table of Contents

1. [Architecture & Pipeline](#1-architecture--pipeline)
2. [Supported Platforms & Scraper Registry](#2-supported-platforms--scraper-registry)
3. [Module Breakdown & File Responsibilities](#3-module-breakdown--file-responsibilities)
4. [Core Features & Extraction Engine](#4-core-features--extraction-engine)
5. [Standardized Response Schema](#5-standardized-response-schema)
6. [Programmatic Usage & Code Examples](#6-programmatic-usage--code-examples)
7. [How to Add a New Store Scraper](#7-how-to-add-a-new-store-scraper)
8. [Testing & Quality Assurance](#8-testing--quality-assurance)

---

## 1. Architecture & Pipeline

```text
Incoming Product URL
        │
        ▼
[router.py] ──────────► detect_platform_from_url()
        │
        ▼
[Store-Specific Scraper] (e.g., AmazonScraper, FlipkartScraper)
        │
        ├──► 1. Extract Store Product Identifier (ASIN, PID, StyleId)
        │
        ├──► 2. [playwright_manager.py] Render dynamic DOM / ScraperAPI Fallback
        │          ├── Anti-Bot Stealth Evasions (mask navigator.webdriver)
        │          ├── Wait for product selectors (title, price, image gallery)
        │          └── Scroll lazy-loaded images into viewport
        │
        ├──► 3. Multi-Source Extraction & Parsing
        │          ├── Priority 1: Scoped Container DOM Elements
        │          ├── Priority 2: JSON-LD Structured Data (<script type="application/ld+json">)
        │          └── Priority 3: OpenGraph & Twitter Meta Tags
        │
        ├──► 4. Sanitization & Normalization
        │          ├── parse_price() -> Filters out EMI, coupons, cashback
        │          ├── normalize_image_url() -> Converts protocol-relative URLs & upscales resolution
        │          └── calculate_discount() -> ((MRP - Price) / MRP) * 100
        │
        ├──► 5. [confidence.py] Confidence Engine Validation (0–100 score)
        │
        ▼
[Standardized JSON Response] (Sent to FastAPI Routes / DB / Celery Workers)
```

---

## 2. Supported Platforms & Scraper Registry

| Platform | Store Code | Dedicated Module | Scraper Class | Identifier Extracted | URL Patterns |
|---|---|---|---|---|---|
| **Amazon India** | `amazon` | `amazon.py` | `AmazonScraper` | 10-char **ASIN** | `amazon.in/dp/B0...`, `amzn.in/d/...`, `gp/product/...` |
| **Flipkart** | `flipkart` | `flipkart.py` | `FlipkartScraper` | **PID** / **FSID** | `flipkart.com/.../p/itm...`, `?pid=...` |
| **Myntra** | `myntra` | `myntra.py` | `MyntraScraper` | **Style ID** | `myntra.com/.../12345678/buy` |
| **AJIO** | `ajio` | `ajio.py` | `AjioScraper` | **Product Code** | `ajio.com/.../p/460788224_black` |
| **Nykaa** | `nykaa` | `nykaa.py` | `NykaaScraper` | **SKU / Product ID** | `nykaa.com/.../p/123456`, `?productId=...` |

---

## 3. Module Breakdown & File Responsibilities

### 🧱 Infrastructure & Core Utilities

- **`base_scraper.py`**:
  Abstract base class (`BaseScraper`) that defines standard contracts for all store scrapers. Includes shared helper utilities:
  - `extract_json_ld(soup)`: Robust JSON-LD parser extracting schema.org `Product` / `@graph` objects.
  - `parse_price(text)`: Converts formatted currency strings (e.g., `₹ 1,49,900.00`) into clean floats while discarding EMI, per-month prices, and cashback text.
  - `clean_title(raw_title)`: Strips e-commerce boilerplate suffixes (`: Buy Online at Best Price...`, `- Flipkart.com`).
  - `sanitize_image_url(url)`: Resolves protocol-relative URLs (`//...`), converts relative paths to absolute URLs, and filters out `1x1` tracking pixels, SVGs, and base64 placeholders.

- **`playwright_manager.py`**:
  Singleton browser manager providing dynamic JavaScript execution via headless Chromium:
  - Injects anti-bot stealth scripts (`navigator.webdriver` mask, realistic browser plugins and languages).
  - Triggers lazy-loaded image hydration by scrolling gallery locators into viewport.
  - Automatically falls back to **ScraperAPI** proxy when anti-bot challenges or blocked shells are detected.

- **`confidence.py`**:
  Heuristic validation engine (`ConfidenceEngine`):
  - Assigns weighted scores (0 to 100) based on title agreement, price sanity, image presence, and store identifier matching.
  - Categorizes extraction state as `verified`, `needs_verification`, or `extraction_failed`.

- **`router.py`**:
  Central routing mechanism (`detect_platform_from_url` and `route_and_scrape`):
  - Automatically inspects the URL domain and routes the request to the matching scraper.

- **`__init__.py`**:
  Package registry exposing `SCRAPER_REGISTRY`, `get_scraper_for_url()`, and top-level helper imports.

---

## 4. Core Features & Extraction Engine

### 🖼️ 1. Multi-Stage High-Resolution Image Extraction
The scrapers employ a 6-tier fallback mechanism to extract the true product image:
1. **Gallery DOM Selectors**: Targets platform-specific product gallery containers.
2. **Attribute Inspection**: Checks `src`, `data-src`, `data-lazy-src`, `data-original`.
3. **`srcset` High-Resolution Resolution Selection**: Parses `srcset` descriptors to select the highest resolution available.
4. **Thumbnail Upscaling**: Upscales thumbnail dimensions (e.g., converting `/image/128/128/` to `/image/832/832/` on Flipkart).
5. **JSON-LD Schema**: Extracts `image` strings or image arrays from structured product schemas.
6. **OpenGraph / Twitter Tags**: Extracts `og:image` or `twitter:image` metadata.

### 💰 2. MRP & Discount Calculation
- Identifies original list prices (MRP) from strike-through pricing elements (`yRaY8j`, `_3I9_wc`, `corePrice_feature_div`).
- Automatically computes exact discount percentages:
  $$\text{Discount \%} = \text{round}\left(\frac{\text{original\_price} - \text{current\_price}}{\text{original\_price}} \times 100\right)$$

### 🛡️ 3. Anti-Bot Resiliency
- Built-in headless Playwright browser automation with stealth masks.
- Seamless fallback to residential proxy network (**ScraperAPI**) for challenging pages.

---

## 5. Standardized Response Schema

Every scraper method (`scrape_amazon`, `scrape_flipkart`, `route_and_scrape`) returns a standardized dictionary:

```json
{
  "platform": "flipkart",
  "title": "Mivi Play 12HRS Playback, Bass Boosted, TWS Feature, IPX4 5 W Portable Bluetooth Speaker",
  "current_price": 899.0,
  "price": 899.0,
  "currency": "INR",
  "original_price": 1999.0,
  "discount_percentage": 55.0,
  "image": "https://rukminim2.flixcart.com/image/832/832/xif0q/speaker/blue/...jpeg?q=70",
  "product_image": "https://rukminim2.flixcart.com/image/832/832/xif0q/speaker/blue/...jpeg?q=70",
  "url": "https://www.flipkart.com/.../p/itm...pid=ACCG6TG4NZHGYWGM",
  "product_id": "ACCG6TG4NZHGYWGM",
  "availability": "in_stock",
  "confidence_score": 95,
  "status": "verified",
  "fetched_at": "2026-08-27T14:00:00Z",
  "success": true,
  "error": null
}
```

---

## 6. Programmatic Usage & Code Examples

### Asynchronous Usage (via Router)
```python
import asyncio
from scrapers.router import route_and_scrape

async def fetch():
    url = "https://www.flipkart.com/boat-rockerz-450-bluetooth-headset/p/itm213a8aa728e57?pid=ACCFSDGGFYAGSZGH"
    result = await route_and_scrape(url)
    print(f"Title: {result['title']}")
    print(f"Price: ₹{result['current_price']} (MRP: ₹{result['original_price']})")
    print(f"Discount: {result['discount_percentage']}% OFF")
    print(f"Image: {result['image']}")

asyncio.run(fetch())
```

### Direct Store Scraper Usage
```python
import asyncio
from scrapers.amazon import AmazonScraper
from scrapers.flipkart import FlipkartScraper

async def scrape_direct():
    fk_scraper = FlipkartScraper()
    res = await fk_scraper.extract_product("https://www.flipkart.com/...pid=ACCG6TG4NZHGYWGM")
    print("Flipkart Success:", res.success)
    print("Flipkart Title:", res.title)

asyncio.run(scrape_direct())
```

### Synchronous Service Call (Used by API & Celery)
```python
from services.platform_fetcher import fetch_product_data

data = fetch_product_data("https://www.amazon.in/dp/B0C5X2MGX3")
if data.success:
    print(f"Product: {data.product_name} - ₹{data.current_price}")
```

---

## 7. How to Add a New Store Scraper

To add support for a new e-commerce store (e.g., `Tata CLiQ`, `Meesho`):

1. **Add Platform Enum**:
   Update `db/models.py` to add the new store enum (e.g., `tatacliq = "tatacliq"`).

2. **Create Store Scraper Module (`backend/scrapers/tatacliq.py`)**:
   Subclass `BaseScraper`:
   ```python
   from scrapers.base_scraper import BaseScraper, ExtractionResult
   from db.models import PlatformEnum

   class TataCliqScraper(BaseScraper):
       store = PlatformEnum.tatacliq

       def extract_product_id(self, url: str) -> Optional[str]:
           # Extract product SKU from URL
           ...

       def get_main_container(self, soup):
           # Return main product container element
           ...

       async def extract_product(self, url: str) -> ExtractionResult:
           # Fetch HTML via PlaywrightManager and extract title, price, image
           ...
   ```

3. **Register in `scrapers/__init__.py` and `router.py`**:
   - Add domain detection keyword in `router.py` (`detect_platform_from_url`).
   - Add instance to `SCRAPER_REGISTRY` in `__init__.py`.

4. **Write Unit Tests (`backend/tests/test_scrapers.py`)**:
   Add test fixture with sample HTML and assert title, price, MRP, and image parsing.

---

## 8. Testing & Quality Assurance

Run the automated test suite inside the Docker backend container:

```bash
docker compose exec backend pytest
```

To run only the scrapers test suite:

```bash
docker compose exec backend pytest tests/test_scrapers.py -v
```
