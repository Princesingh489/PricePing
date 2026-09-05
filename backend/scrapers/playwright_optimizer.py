"""
Playwright Optimizer (High Speed Scraping Engine)
==================================================
Creates an isolated Playwright Page context configured with aggressive network route interception.
Blocks resource types (images, media, fonts, stylesheets, websockets) and aborts telemetry trackers
to reduce bandwidth consumption by >80% and drop page load times from 25s+ to 1-3s.
"""

from __future__ import annotations
import logging
from typing import Set, Tuple
from playwright.async_api import Browser, BrowserContext, Page, Route, Request

logger = logging.getLogger(__name__)

# Resource types that provide zero value for HTML and JSON state extraction
BLOCKED_RESOURCE_TYPES: Set[str] = {
    "image",
    "media",
    "font",
    "stylesheet",
    "websocket",
    "other",  # Favicons, ping beacons, manifest files
}

# Known tracking, analytics, and telemetry domains that delay page completion
BLOCKED_ANALYTICS_DOMAINS: Tuple[str, ...] = (
    "google-analytics.com",
    "googletagmanager.com",
    "doubleclick.net",
    "adservice.google.com",
    "facebook.net",
    "facebook.com/tr",
    "connect.facebook.net",
    "criteo.com",
    "criteo.net",
    "branch.io",
    "appsflyer.com",
    "hotjar.com",
    "clarity.ms",
    "newrelic.com",
    "nr-data.net",
    "amazon-adsystem.com",
    "scorecardresearch.com",
    "omtrdc.net",
    "tiqcdn.com",
    "demdex.net",
    "taboola.com",
    "outbrain.com",
    "bing.com/bat.js",
    "bat.bing.com",
    "ads.pubmatic.com",
    "rubiconproject.com",
    "quantserve.com",
)


async def intercept_and_filter_requests(route: Route, request: Request) -> None:
    """
    Route interception handler executed for each network request.
    Aborts non-essential assets and ad trackers instantly before network transmission.
    """
    try:
        # 1. Block by resource type
        if request.resource_type in BLOCKED_RESOURCE_TYPES:
            await route.abort()
            return

        # 2. Block by telemetry / advertising domain
        req_url = request.url.lower()
        if any(domain in req_url for domain in BLOCKED_ANALYTICS_DOMAINS):
            await route.abort()
            return

        # 3. Allow essential HTML, script, and API fetch/XHR
        await route.continue_()
    except Exception:
        # If route has already been aborted or handled, ignore
        pass


async def create_optimized_page(browser: Browser) -> Page:
    """
    Spawns an isolated BrowserContext and Page configured for ultra-fast scraping.

    Optimizations:
    - Custom User-Agent & realistic desktop client headers.
    - Route interception blocking images, fonts, styles, websockets, and trackers.
    - Anti-bot stealth initialization script.
    - Returns the prepared Page object ready for ultra-fast navigation.
    """
    context: BrowserContext = await browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Safari/537.36"
        ),
        viewport={"width": 1920, "height": 1080},
        locale="en-IN",
        timezone_id="Asia/Kolkata",
        has_touch=False,
        is_mobile=False,
        java_script_enabled=True,
        extra_http_headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
            "DNT": "1",
            "Sec-Ch-Ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        }
    )

    page: Page = await context.new_page()

    # Apply anti-bot stealth evasions
    await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        window.navigator.chrome = { runtime: {} };
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
        Object.defineProperty(navigator, 'languages', { get: () => ['en-IN', 'en-GB', 'en-US', 'en'] });
    """)

    # Attach aggressive network route interceptor
    await page.route("**/*", intercept_and_filter_requests)

    return page
