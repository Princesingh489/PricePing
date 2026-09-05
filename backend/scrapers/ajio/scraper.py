"""
AJIO Scraper Implementation
"""
import re
from typing import Optional
from bs4 import BeautifulSoup, Tag

from db.models import PlatformEnum, AvailabilityEnum
from scrapers.base import BaseScraper
from scrapers.shared.models import ExtractionResult, ExtractionDebug
from scrapers.shared.normalizers import SharedNormalizer
from scrapers.shared.confidence import ConfidenceEngine
from scrapers.ajio import selectors
from scrapers.ajio.extractors import AjioExtractor
from scrapers.ajio.validators import AjioValidator


class AjioScraper(BaseScraper):
    store = PlatformEnum.ajio
    wait_selector = "div#appContainer, div#app, script[type='application/ld+json'], h1.prod-title, div.prod-sp, div.prod-content"

    def extract_product_id(self, url: str) -> Optional[str]:
        """Extract AJIO product code (e.g. 460788224_black, 443666961_olive, 469123456)."""
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

    def get_main_container(self, soup: BeautifulSoup) -> Optional[Tag]:
        for sel in selectors.MAIN_CONTAINER_SELECTORS:
            elem = soup.select_one(sel)
            if elem:
                return elem
        return None

    def extract_from_html(self, html: str, url: str) -> ExtractionResult:
        soup = BeautifulSoup(html, "lxml")
        container = self.get_main_container(soup)
        target = container or soup

        product_id = self.extract_product_id(url)

        # 1. Candidates & Metadata (JSON-LD + preloaded state + visible DOM)
        candidates, meta_data = AjioExtractor.extract_candidates(soup, target)

        # 2. Brand & Title
        brand = AjioExtractor.extract_brand(target)
        if not brand:
            brand = meta_data.get("json_ld_brand") or meta_data.get("preloaded_brand") or meta_data.get("og_brand")

        title = None
        for sel in selectors.TITLE_SELECTORS:
            elem = target.select_one(sel)
            if elem:
                p_name = SharedNormalizer.clean_title(elem.get_text())
                if p_name:
                    title = f"{brand} {p_name}".strip() if brand and brand.lower() not in p_name.lower() else p_name
                    break

        if not title:
            raw_title = meta_data.get("json_ld_name") or meta_data.get("preloaded_name") or meta_data.get("og_title")
            if raw_title:
                clean_t = SharedNormalizer.clean_title(raw_title)
                title = f"{brand} {clean_t}".strip() if brand and brand.lower() not in clean_t.lower() else clean_t

        if not title and soup.title and soup.title.string:
            clean_page_t = SharedNormalizer.clean_title(soup.title.string)
            if clean_page_t:
                clean_page_t = re.sub(r'\s*\|\s*Ajio\.com.*$', '', clean_page_t, flags=re.IGNORECASE).strip()
                title = clean_page_t

        # 3. Price Ranking & Discount
        raw_price, raw_mrp = AjioValidator.filter_and_rank_prices(candidates)

        extracted_discount = meta_data.get("preloaded_discount")
        if extracted_discount is None:
            for sel in selectors.DISCOUNT_SELECTORS:
                elem = target.select_one(sel)
                if elem:
                    d_match = re.search(r'(\d+)', elem.get_text())
                    if d_match:
                        extracted_discount = float(d_match.group(1))
                        break

        current_price, original_price, discount, saved_amount = ConfidenceEngine.validate_and_calculate_discount(
            raw_price, raw_mrp, extracted_discount
        )

        # 4. Image, Rating & Count
        image_url = AjioExtractor.extract_image(target, soup) or meta_data.get("json_ld_image") or meta_data.get("preloaded_image") or meta_data.get("og_image")
        images = AjioExtractor.extract_images(soup, target)
        if image_url and image_url not in images:
            images.insert(0, image_url)
        elif not image_url and images:
            image_url = images[0]

        rating = meta_data.get("rating")
        if rating is None:
            for sel in selectors.RATING_SELECTORS:
                elem = target.select_one(sel)
                if elem:
                    rating = SharedNormalizer.parse_rating(elem.get_text())
                    if rating is not None:
                        break

        rating_count = meta_data.get("rating_count")
        if rating_count is None:
            for sel in selectors.COUNT_SELECTORS:
                elem = target.select_one(sel)
                if elem:
                    rating_count = SharedNormalizer.parse_count(elem.get_text())
                    if rating_count is not None:
                        break

        # 5. Variant & Availability (Scoped Buybox)
        variant = AjioExtractor.extract_variant(soup, target, url)
        variants = AjioExtractor.extract_variants(
            soup=soup,
            target=target,
            default_price=current_price,
            default_mrp=original_price,
        )
        avail_str, is_buybox_active = AjioExtractor.extract_availability(soup, target)
        if not is_buybox_active and meta_data.get("json_ld_availability") == "in_stock":
            avail_str, is_buybox_active = "in_stock", True
        availability = AvailabilityEnum(avail_str)

        # 6. Confidence Scoring
        field_conf = ConfidenceEngine.calculate_field_confidence(
            selected_price=current_price,
            price_candidates=candidates,
            has_main_container=container is not None or bool(meta_data.get("preloaded_name")) or bool(meta_data.get("json_ld_name")) or bool(meta_data.get("og_title")),
            has_title=bool(title),
            has_image=bool(image_url),
            original_price=original_price,
            discount_percentage=discount,
            rating=rating,
            variant=variant,
            is_buybox_active=is_buybox_active,
        )

        is_page_not_found = bool(
            soup.find(string=re.compile(r"PAGE NOT AVAILABLE|Page Not Found|WHOOPS!", re.I))
            or (soup.title and "not available" in soup.title.string.lower())
        )
        is_uncertain = is_page_not_found or ConfidenceEngine.should_fail_closed(field_conf.overall) or current_price is None or not title
        status = "uncertain" if is_uncertain else "verified"

        err_msg = None
        if is_page_not_found:
            err_msg = "This product is no longer available on AJIO (Page Not Found)."
        elif is_uncertain:
            err_msg = "Unable to reliably verify the current product price"

        debug_info = ExtractionDebug(
            original_url=url,
            normalized_url=url,
            detected_store="ajio",
            extracted_product_id=product_id,
            candidate_prices=[c.to_dict() for c in candidates],
            confidence_score=field_conf.overall if not is_page_not_found else 0,
            status=status,
        )

        return ExtractionResult(
            store=PlatformEnum.ajio,
            store_product_id=product_id,
            title=title,
            brand=brand,
            current_price=current_price,
            original_price=original_price,
            discount_percentage=discount,
            saved_amount=saved_amount,
            image_url=image_url,
            images=images,
            rating=rating,
            rating_count=rating_count,
            review_count=meta_data.get("review_count"),
            currency="INR",
            availability=availability if not is_page_not_found else AvailabilityEnum.unavailable,
            variant=variant or None,
            variants=variants,
            confidence_score=field_conf.overall if not is_page_not_found else 0,
            field_confidence=field_conf,
            status=status,
            debug_info=debug_info,
            success=not is_uncertain,
            error_message=err_msg,
            product_url=url,
        )
