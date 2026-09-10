import asyncio
import logging
import httpx
from typing import Optional, Tuple
from core.config import settings

logger = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"


class PlaywrightManager:
    """
    Manages Playwright browser automation with explicit waits, anti-bot settings,
    and automatic resilient fallback to ScraperAPI / HTTP client when needed.
    """

    @classmethod
    async def fetch_html(cls, url: str, wait_selector: Optional[str] = None, timeout_ms: int = 20000) -> Tuple[Optional[str], str]:
        """
        Fetches the rendered HTML of a dynamic product page.
        Returns: (html_content: Optional[str], fetch_method: str)
        """
        # 1. Try warm PlaywrightPool browser (fast, local headless Chromium with blocked ads/trackers)
        try:
            from scrapers.playwright_pool import PlaywrightPool
            html, method = await PlaywrightPool.fetch_html(url, wait_selector=wait_selector, timeout_ms=min(timeout_ms, 12000))
            if html and len(html) > 1000:
                return html, method
        except Exception as e:
            logger.warning(f"PlaywrightPool fetch failed for {url}: {e}. Proceeding to fallback.")

        # 2. Try Host Browser Bridge only if port 8765 is actively listening (sub-millisecond socket check)
        try:
            r, w = await asyncio.wait_for(asyncio.open_connection("127.0.0.1", 8765), timeout=0.1)
            w.close()
            await w.wait_closed()
            import urllib.parse
            encoded_target = urllib.parse.quote(url, safe="")
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(f"http://127.0.0.1:8765/render?url={encoded_target}")
                if resp.status_code == 200 and len(resp.text) > 3000:
                    logger.info(f"Host browser bridge rendered {url} successfully ({len(resp.text)} bytes)")
                    return resp.text, "host_browser"
        except Exception:
            pass

        # 3. Try ScraperAPI fallback if configured
        scraper_api_key = getattr(settings, 'SCRAPER_API_KEY', '')
        if scraper_api_key:
            try:
                import urllib.parse
                encoded_target = urllib.parse.quote(url, safe="")
                api_url = f"http://api.scraperapi.com?api_key={scraper_api_key}&url={encoded_target}"
                async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
                    resp = await client.get(api_url)
                    if resp.status_code == 200 and len(resp.text) > 3000:
                        logger.info(f"ScraperAPI fetched {url} successfully ({len(resp.text)} bytes)")
                        return resp.text, "scraper_api"
            except Exception as e:
                logger.warning(f"ScraperAPI fetch failed for {url}: {e}")

        # 3. Try Direct Async HTTP fetch with browser headers
        try:
            headers = {
                "User-Agent": USER_AGENT,
                "Accept-Language": "en-IN,en-GB;q=0.9,en;q=0.8",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Sec-Ch-Ua": '"Chromium";v="125", "Not.A/Brand";v="24"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
            }
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, headers=headers) as client:
                resp = await client.get(url)
                if resp.status_code == 200 and len(resp.text) > 2000:
                    logger.info(f"Direct HTTP fetched {url} successfully ({len(resp.text)} bytes)")
                    return resp.text, "direct_http"
        except Exception as e:
            logger.warning(f"Direct HTTP fetch failed for {url}: {e}")

        return None, "none"
