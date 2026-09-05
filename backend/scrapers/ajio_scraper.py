"""
AJIO India Scraper
==================
High-accuracy scraper for AJIO.com using multi-source verification (DOM, JSON-LD, Metadata), candidate price classification, and high-res image extraction.
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


class AjioScraper(BaseScraper):
    store = PlatformEnum.ajio

    def extract_product_id(self, url: str) -> Optional[str]:
        """Extract AJIO product code (e.g. 460123456_blue)."""
        if not url:
            return None
        patterns = [
            r'/p/([a-zA-Z0-9_-]+)',
            r'productCode=([a-zA-Z0-9_-]+)',
        ]
        for pat in patterns:
            m = re.search(pat, url)
            if m:
                return m.group(1)
        return None

    def get_main_container(self, soup: BeautifulSoup) -> Optional[Tag]:
        return DomExtractor.get_main_container(soup, PlatformEnum.ajio)

    def extract_from_html(self, html: str, url: str) -> ExtractionResult:
        """Parse AJIO product page HTML."""
        soup = BeautifulSoup(html, "lxml")
        container = self.get_main_container(soup)
        target = container or soup

        product_id = self.extract_product_id(url)
        json_ld_data = JsonLdExtractor.extract_product_data(soup)
        meta_data = MetaExtractor.extract_metadata(soup)
        extraction_sources: Dict[str, str] = {}

        # 1. Title Extraction
        title = None
        brand_elem = target.select_one("h2.brand-name, h2.prod-brand")
        name_elem = target.select_one("h1.prod-title, h1.prod-name")

        if brand_elem and name_elem:
            b = brand_elem.get_text().strip()
            n = name_elem.get_text().strip()
            title = self.clean_title(f"{b} {n}")
            if title:
                extraction_sources["title"] = "visible_main_dom"
        elif name_elem:
            title = self.clean_title(name_elem.get_text())
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

        if not title:
            for script in soup.find_all("script"):
                txt = script.string or script.get_text() or ""
                if "window.__PRELOADED_STATE__" in txt:
                    try:
                        idx = txt.find("window.__PRELOADED_STATE__")
                        eq_idx = txt.find("=", idx)
                        if eq_idx != -1:
                            import json
                            json_str = txt[eq_idx + 1:].strip().rstrip(";")
                            data = json.loads(json_str)
                            if isinstance(data, dict):
                                prod = data.get("product")
                                pd = prod.get("productDetails") if isinstance(prod, dict) else None
                                if not isinstance(pd, dict):
                                    pd = data.get("productDetails")
                                if isinstance(pd, dict):
                                    p_name = pd.get("name")
                                    b_name = pd.get("brandName")
                                    if p_name:
                                        full_t = f"{b_name} {p_name}" if b_name and b_name.lower() not in p_name.lower() else p_name
                                        title = self.clean_title(full_t)
                                        if title:
                                            extraction_sources["title"] = "preloaded_state"
                    except Exception:
                        pass
                    break

        # 2. Candidate Price Extraction & Classification
        candidates = PriceExtractor.extract_candidates(
            soup=soup,
            container=container,
            platform=PlatformEnum.ajio,
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
        disc_elem = target.select_one(".prod-discnt, .discount-percent")
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
            platform=PlatformEnum.ajio,
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
            platform=PlatformEnum.ajio,
            json_ld_data=json_ld_data,
        )
        if rating is not None:
            extraction_sources["rating"] = "visible_main_dom"

        # 5. Availability
        availability = DomExtractor.extract_availability(target, PlatformEnum.ajio)

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
            detected_store="ajio",
            extracted_product_id=product_id,
            candidate_prices=[c.to_dict() for c in candidates],
            extraction_sources=extraction_sources,
            confidence_score=confidence,
            status=status,
        )

        return ExtractionResult(
            store=PlatformEnum.ajio,
            store_product_id=product_id,
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
                wait_selector="h1.prod-title, div.prod-sp, div.prod-content",
                timeout_ms=15000,
            )
        except Exception as e:
            logger.debug(f"Playwright fetch failed for AJIO: {e}")

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
                logger.error(f"HTTP fallback failed for AJIO: {e}")

        if not html:
            return ExtractionResult(
                store=PlatformEnum.ajio,
                store_product_id=self.extract_product_id(url),
                status="uncertain",
                success=False,
                error_message="Failed to load page content",
                product_url=url,
            )

        return self.extract_from_html(html, url)


# Alias function
async def scrape_ajio(url: str) -> ExtractionResult:
    scraper = AjioScraper()
    return await scraper.extract_product(url)
