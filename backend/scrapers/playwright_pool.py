"""
Playwright Reusable Browser Pool & Resource Blocker
===================================================
Manages persistent browser automation with route filtering to abort ads, trackers, videos,
and analytics, accelerating DOM hydration and targeted price extraction.
Reuses warm browser instances to eliminate cold-start overhead (~2-4 seconds saved per call).
"""
import asyncio
import logging
from typing import Optional, Tuple
from core.config import settings

logger = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"

# Resources to block to speed up page rendering (never block stylesheets as CSSOM is needed for DOM hydration)
BLOCKED_RESOURCE_TYPES = {"image", "media", "font"}
BLOCKED_DOMAINS = [
    "google-analytics.com",
    "doubleclick.net",
    "facebook.net",
    "scorecardresearch.com",
    "hotjar.com",
    "clarity.ms",
    "criteo.com",
    "adsystem.com",
    "adsrvr.org",
]


class PlaywrightPool:
    """
    High-performance Playwright extraction helper with warm browser pooling and route interception.
    """
    _playwright = None
    _browser = None
    _lock = asyncio.Lock()
    _semaphore = asyncio.Semaphore(1)  # Strict limit: Max 1 concurrent browser tab to protect RAM

    @classmethod
    async def _get_browser(cls):
        """Get or lazily launch the persistent shared Chromium browser with memory limits."""
        if cls._browser and cls._browser.is_connected():
            return cls._browser

        async with cls._lock:
            # Double check after lock acquisition
            if cls._browser and cls._browser.is_connected():
                return cls._browser

            try:
                from playwright.async_api import async_playwright
                if not cls._playwright:
                    cls._playwright = await async_playwright().start()

                logger.info("Initializing memory-capped Playwright Chromium browser instance...")
                cls._browser = await cls._playwright.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-gpu",
                        "--renderer-process-limit=1",
                        "--js-flags=--max-old-space-size=256",
                        "--disable-extensions",
                        "--disable-background-networking",
                        "--disable-sync",
                        "--disable-default-apps",
                        "--mute-audio",
                        "--no-first-run",
                        "--window-size=1280,720",
                    ]
                )
                return cls._browser
            except Exception as e:
                logger.error(f"Failed to launch Playwright browser: {e}")
                cls._browser = None
                return None

    @classmethod
    async def fetch_html(
        cls,
        url: str,
        wait_selector: Optional[str] = None,
        timeout_ms: int = 8000,
        block_heavy_media: bool = True,
    ) -> Tuple[Optional[str], str]:
        """
        Fetches rendered HTML using warm Playwright Chromium with stealth context.
        Guarded by a concurrency semaphore to prevent RAM spikes on low-resource EC2 servers.
        """
        # Acquire semaphore so at most 1 browser task runs at any time
        try:
            async with asyncio.timeout(12.0):
                async with cls._semaphore:
                    context = None
                    try:
                        browser = await cls._get_browser()
                        if not browser:
                            return None, "none"

                        context = await browser.new_context(
                            user_agent=USER_AGENT,
                            viewport={"width": 1280, "height": 720},
                            locale="en-IN",
                            timezone_id="Asia/Kolkata",
                            extra_http_headers={
                                "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
                                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                                "Sec-Ch-Ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
                                "Sec-Ch-Ua-Mobile": "?0",
                                "Sec-Ch-Ua-Platform": '"Windows"',
                                "Upgrade-Insecure-Requests": "1",
                            }
                        )
                        page = await context.new_page()

                        # Stealth evasion scripts
                        await page.add_init_script("""
                            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                            window.navigator.chrome = { runtime: {} };
                        """)

                        # Route abortion for heavy trackers & ads
                        if block_heavy_media:
                            async def route_interceptor(route):
                                req = route.request
                                if req.resource_type in BLOCKED_RESOURCE_TYPES or any(d in req.url for d in BLOCKED_DOMAINS):
                                    await route.abort()
                                else:
                                    await route.continue_()

                            await page.route("**/*", route_interceptor)

                        logger.info(f"Playwright targeted navigation to {url} (warm context)...")
                        await page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)

                        # Targeted wait if selector provided
                        if wait_selector:
                            try:
                                await page.wait_for_selector(wait_selector, timeout=min(timeout_ms, 3500))
                            except Exception:
                                pass

                        # Brief pause for dynamic hydration
                        try:
                            await page.wait_for_timeout(300)
                        except Exception:
                            pass

                        content = await page.content()
                        if content and len(content) > 1000:
                            return content, "playwright"

                    except Exception as e:
                        logger.warning(f"PlaywrightPool fetch error for {url}: {e}")
                    finally:
                        if context:
                            try:
                                await context.close()
                            except Exception:
                                pass
        except (TimeoutError, asyncio.TimeoutError):
            logger.warning(f"PlaywrightPool semaphore wait timed out for {url}")
        except Exception as err:
            logger.warning(f"PlaywrightPool unexpected error: {err}")

        return None, "none"

    @classmethod
    async def close_pool(cls):
        """Cleanly terminate shared browser instance upon app shutdown."""
        async with cls._lock:
            if cls._browser:
                try:
                    await cls._browser.close()
                except Exception:
                    pass
                cls._browser = None
            if cls._playwright:
                try:
                    await cls._playwright.stop()
                except Exception:
                    pass
                cls._playwright = None
