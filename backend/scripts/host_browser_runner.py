"""
PricePing Host Browser Runner
=============================
High-performance host browser bridge running off-screen Chrome on Windows.
Bypasses Akamai/Cloudflare bot protection by utilizing real host Chrome environment.
Listens on 0.0.0.0:8765 for requests from the backend container (via host.docker.internal).
"""
import asyncio
import json
import logging
import re
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("host_browser_runner")

_pw = None
_browser = None
_is_cdp = False
_lock = asyncio.Lock()


def extract_ajio_code(url: str) -> Optional[str]:
    if not url:
        return None
    patterns = [
        r'/p/([a-zA-Z0-9_-]+)',
        r'[?&](?:productCode|code|prodId)=([a-zA-Z0-9_-]+)',
        r'([0-9]{9,10}_[a-zA-Z0-9]+)',
        r'/([0-9]{9,10})(?:[/?#]|$)',
    ]
    for pat in patterns:
        m = re.search(pat, url)
        if m:
            return m.group(1)
    return None


def build_ajio_html(data: dict, url: str) -> str:
    name = data.get("name", "")
    brand = data.get("brandName", "")
    price_info = data.get("price") or {}
    was_price = data.get("wasPriceData") or {}
    price_val = price_info.get("value")
    mrp_val = was_price.get("value") or price_val
    discount = price_info.get("discountValue") or 0
    stock_status = data.get("stock", {}).get("stockLevelStatus", "inStock")
    is_in_stock = stock_status == "inStock"

    # Images - collect high-res 'product' format images (473Wx593H)
    product_images = []
    other_images = []
    for img in data.get("images", []):
        u = img.get("url")
        fmt = img.get("format", "")
        if not u or "trust_marker" in u.lower() or "logo" in u.lower() or u.endswith(".svg"):
            continue
        if fmt == "product" or "473w" in u.lower():
            if u not in product_images:
                product_images.append(u)
        elif fmt in ("superZoomPdp", "mobileProductListingImage", "thumbnail"):
            if u not in other_images:
                other_images.append(u)

    images = product_images if product_images else other_images
    main_image = images[0] if images else ""

    # Variants (sizes)
    variants = []
    for vo in data.get("variantOptions", []):
        sz = None
        for q in vo.get("variantOptionQualifiers", []):
            if q.get("qualifier") == "size" or q.get("name") == "Size*":
                sz = q.get("value")
                break
        if sz:
            p_data = vo.get("priceData") or {}
            v_price = p_data.get("value") or price_val
            st = vo.get("stock") or {}
            in_st = st.get("stockLevelStatus") != "outOfStock"
            variants.append({
                "@type": "Product",
                "name": f"{brand} {name} - Size {sz}",
                "size": sz,
                "offers": {
                    "@type": "Offer",
                    "price": str(v_price),
                    "priceCurrency": "INR",
                    "availability": "https://schema.org/InStock" if in_st else "https://schema.org/OutOfStock",
                    "highPrice": str(mrp_val) if mrp_val else None,
                }
            })

    json_ld = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": name,
        "brand": {"@type": "Brand", "name": brand},
        "image": main_image,
        "offers": {
            "@type": "Offer",
            "price": str(price_val) if price_val else "0",
            "highPrice": str(mrp_val) if mrp_val else str(price_val),
            "priceCurrency": "INR",
            "availability": "https://schema.org/InStock" if is_in_stock else "https://schema.org/OutOfStock",
        },
        "hasVariant": variants,
    }

    img_tags = "".join([f'<img class="preview-image" src="{img}" />' for img in images[:12]])

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Buy {brand} {name} Online | Ajio.com</title>
    <meta property="og:title" content="{brand} {name}" />
    <meta property="og:image" content="{main_image}" />
    <script type="application/ld+json">
    {json.dumps(json_ld)}
    </script>
</head>
<body>
    <div id="appContainer">
        <h2 class="brand-name">{brand}</h2>
        <h1 class="prod-title">{name}</h1>
        <div class="prod-sp">₹{price_val}</div>
        <span class="prod-cp">₹{mrp_val}</span>
        <span class="prod-discnt">{discount}% off</span>
        <div class="img-holder">
            {img_tags}
        </div>
        <div class="btn-gold">Add to Bag</div>
    </div>
    <script>
    window.__PRELOADED_STATE__ = {json.dumps({"product": {"productDetails": data}})};
    </script>
</body>
</html>"""
    return html


async def get_browser():
    global _pw, _browser, _is_cdp
    if _browser and _browser.is_connected():
        return _browser
    async with _lock:
        if _browser and _browser.is_connected():
            return _browser
        if not _pw:
            _pw = await async_playwright().start()

        # Priority 1: Connect to running Chrome on 127.0.0.1:9222 (active session with warm cookies)
        try:
            logger.info("Attempting connection to active Chrome over CDP on 127.0.0.1:9222...")
            _browser = await _pw.chromium.connect_over_cdp("http://127.0.0.1:9222")
            _is_cdp = True
            logger.info("Successfully connected to active Chrome over CDP (port 9222)!")
            return _browser
        except Exception as cdp_err:
            logger.info(f"CDP connection to port 9222 unavailable ({cdp_err}). Launching standalone off-screen Chrome...")

        # Priority 2: Launch standalone Chrome with anti-detection flags
        _browser = await _pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--window-position=-2500,-2500",
                "--window-size=1280,800",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ]
        )
        _is_cdp = False
        return _browser


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await get_browser()
        logger.info("Host browser bridge ready on port 8765.")
    except Exception as e:
        logger.warning(f"Failed to pre-warm browser: {e}")
    yield
    global _pw, _browser
    if _browser:
        await _browser.close()
    if _pw:
        await _pw.stop()


app = FastAPI(title="PricePing Host Browser Bridge", lifespan=lifespan)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "host_browser_runner",
        "is_cdp": _is_cdp,
        "browser_connected": _browser.is_connected() if _browser else False,
    }


@app.get("/render", response_class=HTMLResponse)
async def render(
    url: str = Query(..., description="Target URL to render with host Chrome"),
    wait_selector: Optional[str] = Query(None, description="CSS selector to wait for"),
    timeout_ms: int = Query(15000, description="Max render timeout in ms")
):
    browser = await get_browser()
    
    # Get or create context
    if _is_cdp and browser.contexts:
        context = browser.contexts[0]
        page = await context.new_page()
        should_close_context = False
    else:
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        )
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await context.new_page()
        should_close_context = True

    try:
        # Specialized fast-path for AJIO products
        if "ajio.com" in url:
            ajio_code = extract_ajio_code(url)
            if ajio_code:
                api_url = f"https://www.ajio.com/api/p/{ajio_code}"
                logger.info(f"Using AJIO direct API endpoint: {api_url}")
                try:
                    await page.goto(api_url, timeout=timeout_ms)
                    raw_text = await page.inner_text("body")
                    if raw_text and raw_text.strip().startswith("{"):
                        data = json.loads(raw_text)
                        if data and data.get("name") and data.get("price"):
                            html = build_ajio_html(data, url)
                            logger.info(f"Successfully generated AJIO verified HTML for {ajio_code} ({len(html)} bytes)")
                            return HTMLResponse(content=html, status_code=200)
                        elif data == {} or not data.get("name"):
                            # Product is 404 / deleted / not found
                            logger.warning(f"AJIO product {ajio_code} not found (empty API response)")
                            return HTMLResponse(
                                content="<html><head><title>WHOOPS! PAGE NOT AVAILABLE | Ajio.com</title></head><body><h1>WHOOPS! PAGE NOT AVAILABLE</h1><p>Product not found</p></body></html>",
                                status_code=404,
                            )
                except Exception as api_err:
                    logger.warning(f"AJIO API fetch failed: {api_err}. Falling back to page navigation.")

        # Standard navigation for other platforms or fallback
        logger.info(f"Navigating via host Chrome: {url}")
        resp = await page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        status_code = resp.status if resp else 200

        # Wait for dynamic React content
        sel = wait_selector or "div#appContainer, div.prod-sp, h1.prod-title, div.pdp-details, div[class*='pdp-container']"
        try:
            await page.wait_for_selector(sel, timeout=min(timeout_ms, 4000))
        except Exception:
            pass

        await page.wait_for_timeout(600)
        html = await page.content()
        logger.info(f"Rendered {url}: status={status_code}, length={len(html)}")
        return HTMLResponse(content=html, status_code=status_code)
    except Exception as e:
        logger.error(f"Render error for {url}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await page.close()
        if should_close_context:
            await context.close()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8765, log_level="info")
