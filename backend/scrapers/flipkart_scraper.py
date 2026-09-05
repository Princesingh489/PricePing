"""
Flipkart India Scraper
======================
High-accuracy scraper for Flipkart.com using multi-source verification (DOM, JSON-LD, Metadata), candidate price classification, high-res image upscaling, and rating/review separation.
"""
import re
import json
import logging
from typing import Optional, Dict, Any, List
from bs4 import BeautifulSoup, Tag
from db.models import PlatformEnum, AvailabilityEnum
from scrapers.base_scraper import BaseScraper, ExtractionResult, ExtractionDebug
from scrapers.normalizers import PriceNormalizer, NumberNormalizer
from scrapers.extractors import (
    JsonLdExtractor,
    MetaExtractor,
    DomExtractor,
    PriceExtractor,
    RatingExtractor,
    ImageExtractor,
)
from scrapers.validators import (
    PriceValidator,
    ProductValidator,
    ConfidenceValidator,
)

logger = logging.getLogger(__name__)


class FlipkartScraper(BaseScraper):
    store = PlatformEnum.flipkart

    def extract_product_id(self, url: str) -> Optional[str]:
        """Extract Flipkart PID or item ID (e.g. itm..., PID...)."""
        if not url:
            return None
        patterns = [
            r'[?&]pid=([A-Za-z0-9_-]+)',
            r'/p/([a-zA-Z0-9]+)',
        ]
        for pat in patterns:
            m = re.search(pat, url, re.IGNORECASE)
            if m:
                return m.group(1)
        return None

    def get_main_container(self, soup: BeautifulSoup) -> Optional[Tag]:
        return DomExtractor.get_main_container(soup, PlatformEnum.flipkart)

    normalize_flipkart_image = staticmethod(ImageExtractor.normalize_flipkart_image)
    extract_largest_from_srcset = staticmethod(ImageExtractor.extract_largest_from_srcset)

    def extract_from_html(self, html: str, url: str) -> ExtractionResult:
        """Parse Flipkart product page HTML."""
        soup = BeautifulSoup(html, "lxml")
        container = self.get_main_container(soup)
        target = container or soup

        pid = self.extract_product_id(url)
        json_ld_data = JsonLdExtractor.extract_product_data(soup)
        meta_data = MetaExtractor.extract_metadata(soup)

        if not pid:
            can_link = soup.select_one("link[rel='canonical']")
            if can_link and can_link.get("href"):
                pid = self.extract_product_id(can_link["href"])
            if not pid and json_ld_data.get("sku"):
                pid = str(json_ld_data["sku"]).strip()
        extraction_sources: Dict[str, str] = {}

        # 1. Title Extraction
        title = None
        title_elem = target.select_one("span.VU-ZEz, h1.yhB1nd, span.B_NuCI, h1._6EBuvT span")
        if title_elem:
            title = self.clean_title(title_elem.get_text())
            if title:
                extraction_sources["title"] = "visible_main_dom"

        if not title and json_ld_data.get("title"):
            title = self.clean_title(json_ld_data["title"])
            if title:
                extraction_sources["title"] = "json_ld"

        if not title and meta_data.get("title"):
            title = self.clean_title(meta_data["title"])
            if title:
                extraction_sources["title"] = "meta_og"

        # 2. Candidate Price Extraction & Classification
        candidates = PriceExtractor.extract_candidates(
            soup=soup,
            container=container,
            platform=PlatformEnum.flipkart,
            json_ld_data=json_ld_data,
            meta_data=meta_data,
        )

        current_price = None
        original_price = None
        extracted_discount = None

        # Current Price Candidates
        curr_candidates = [c for c in candidates if c.label == "current_price" and c.confidence_weight > 0]
        if curr_candidates:
            best_curr = max(curr_candidates, key=lambda c: c.confidence_weight)
            current_price = best_curr.value
            extraction_sources["current_price"] = best_curr.source

        # MRP Candidates
        mrp_candidates = [c for c in candidates if c.label == "mrp" and c.confidence_weight > 0]
        if mrp_candidates:
            best_mrp = max(mrp_candidates, key=lambda c: c.confidence_weight)
            original_price = best_mrp.value
            extraction_sources["original_price"] = best_mrp.source

        # Extract discount percentage from DOM
        disc_elem = target.select_one("div.UkUFwK span, div._3Ay6Sb span, div.HQe44n span")
        if disc_elem:
            m = re.search(r'(\d+)\s*%', disc_elem.get_text())
            if m:
                extracted_discount = float(m.group(1))

        # Validate prices & mathematical discount
        current_price, original_price, discount_percentage = PriceValidator.validate_prices(
            current_price=current_price,
            original_price=original_price,
            extracted_discount=extracted_discount,
        )
        if discount_percentage is not None:
            extraction_sources["discount_percentage"] = "calculated_and_verified"

        # 3. High-Resolution Image Extraction
        image_url = ImageExtractor.extract_main_image(
            soup=soup,
            container=container,
            platform=PlatformEnum.flipkart,
            page_url=url,
            json_ld_data=json_ld_data,
            meta_data=meta_data,
        )
        if image_url:
            extraction_sources["image"] = "main_product_gallery"

        # 4. Rating & Counts
        rating, rating_count, review_count = RatingExtractor.extract_ratings_and_counts(
            soup=soup,
            container=container,
            platform=PlatformEnum.flipkart,
            json_ld_data=json_ld_data,
        )
        if rating is not None:
            extraction_sources["rating"] = "visible_main_dom"

        # 5. Availability
        availability = DomExtractor.extract_availability(target, PlatformEnum.flipkart)

        # 6. Confidence Scoring
        confidence = ConfidenceValidator.calculate_confidence(
            selected_price=current_price,
            candidates=candidates,
            has_main_container=container is not None,
            has_title=ProductValidator.validate_title(title),
            has_image=ProductValidator.validate_image(image_url),
            json_ld_price=json_ld_data.get("current_price"),
        )

        # Fail closed check
        is_uncertain = ConfidenceValidator.should_fail_closed(confidence) or current_price is None or not ProductValidator.validate_title(title)
        status = "uncertain" if is_uncertain else "verified"
        error_msg = "Unable to reliably verify the current product price" if is_uncertain else None

        debug_info = ExtractionDebug(
            original_url=url,
            normalized_url=url,
            detected_store="flipkart",
            extracted_product_id=pid,
            candidate_prices=[c.to_dict() for c in candidates],
            extraction_sources=extraction_sources,
            confidence_score=confidence,
            status=status,
        )

        return ExtractionResult(
            store=PlatformEnum.flipkart,
            store_product_id=pid,
            title=title,
            current_price=current_price,
            original_price=original_price,
            discount_percentage=discount_percentage,
            image_url=image_url,
            rating=rating,
            rating_count=rating_count,
            review_count=review_count,
            currency="INR",
            availability=availability,
            confidence_score=confidence,
            status=status,
            extraction_sources=extraction_sources,
            debug_info=debug_info,
            success=not is_uncertain,
            error_message=error_msg,
            product_url=url,
        )

    async def extract_product(self, url: str) -> ExtractionResult:
        """Fetch using Playwright or httpx fallback and extract."""
        html = None
        try:
            from scrapers.playwright_manager import PlaywrightManager
            html, method = await PlaywrightManager.fetch_html(
                url,
                wait_selector="span.VU-ZEz, h1.yhB1nd, div.Nx9bqj, div.DOjaWF",
                timeout_ms=15000,
            )
        except Exception as e:
            logger.debug(f"Playwright fetch failed for Flipkart: {e}")

        if not html:
            import httpx
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
            }
            try:
                async with httpx.AsyncClient(timeout=10, follow_redirects=True, headers=headers) as client:
                    resp = await client.get(url)
                    if resp.status_code == 200:
                        html = resp.text
            except Exception as e:
                logger.error(f"HTTP fallback failed for Flipkart: {e}")

        if not html:
            return ExtractionResult(
                store=PlatformEnum.flipkart,
                store_product_id=self.extract_product_id(url),
                status="uncertain",
                success=False,
                error_message="Failed to load page content",
                product_url=url,
            )

        return self.extract_from_html(html, url)


# Alias function
async def scrape_flipkart(url: str) -> ExtractionResult:
    scraper = FlipkartScraper()
    return await scraper.extract_product(url)
