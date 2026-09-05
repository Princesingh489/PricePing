"""
Myntra Scraper Implementation
"""
import re
from typing import Optional
from bs4 import BeautifulSoup, Tag

from db.models import PlatformEnum, AvailabilityEnum
from scrapers.base import BaseScraper
from scrapers.shared.models import ExtractionResult, ExtractionDebug
from scrapers.shared.normalizers import SharedNormalizer
from scrapers.shared.confidence import ConfidenceEngine
from scrapers.myntra import selectors
from scrapers.myntra.extractors import MyntraExtractor
from scrapers.myntra.validators import MyntraValidator


class MyntraScraper(BaseScraper):
    store = PlatformEnum.myntra
    wait_selector = "h1.pdp-title, h1.pdp-name, span.pdp-price, div.pdp-details"

    def extract_product_id(self, url: str) -> Optional[str]:
        """Extract Myntra numeric product ID from URL."""
        if not url:
            return None
        m = re.search(r'/(\d+)(?:/buy|\?|$)', url)
        return m.group(1) if m else None

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

        # 1. Title & Brand
        brand = MyntraExtractor.extract_brand(target)
        title = None
        title_elem = target.select_one("h1.pdp-name")
        if title_elem:
            p_name = SharedNormalizer.clean_title(title_elem.get_text())
            title = f"{brand} {p_name}".strip() if brand and brand not in (p_name or "") else p_name

        if not title:
            for sel in selectors.TITLE_SELECTORS:
                elem = target.select_one(sel)
                if elem:
                    title = SharedNormalizer.clean_title(elem.get_text())
                    if title:
                        break

        # 2. Candidates
        candidates, meta_data = MyntraExtractor.extract_candidates(soup, target)
        if not title and meta_data.get("json_ld_name"):
            title = SharedNormalizer.clean_title(meta_data["json_ld_name"])
        if not brand and meta_data.get("json_ld_brand"):
            brand = meta_data["json_ld_brand"]

        # 3. Price Ranking & Discount
        raw_price, raw_mrp = MyntraValidator.filter_and_rank_prices(candidates)

        extracted_discount = None
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
        image_url = MyntraExtractor.extract_image(target, soup) or meta_data.get("json_ld_image")
        images = MyntraExtractor.extract_images(soup)
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
        variant = MyntraExtractor.extract_variant(soup, target, url)
        variants = MyntraExtractor.extract_variants(
            soup=soup,
            target=target,
            default_price=current_price,
            default_mrp=original_price,
        )
        avail_str, is_buybox_active = MyntraExtractor.extract_availability(soup, target)
        availability = AvailabilityEnum(avail_str)

        # 6. Confidence Scoring
        field_conf = ConfidenceEngine.calculate_field_confidence(
            selected_price=current_price,
            price_candidates=candidates,
            has_main_container=container is not None,
            has_title=bool(title),
            has_image=bool(image_url),
            original_price=original_price,
            discount_percentage=discount,
            rating=rating,
            variant=variant,
            is_buybox_active=is_buybox_active,
        )

        is_uncertain = ConfidenceEngine.should_fail_closed(field_conf.overall) or current_price is None or not title
        status = "uncertain" if is_uncertain else "verified"

        debug_info = ExtractionDebug(
            original_url=url,
            normalized_url=url,
            detected_store="myntra",
            extracted_product_id=product_id,
            candidate_prices=[c.to_dict() for c in candidates],
            confidence_score=field_conf.overall,
            status=status,
        )

        return ExtractionResult(
            store=PlatformEnum.myntra,
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
            availability=availability,
            variant=variant or None,
            variants=variants,
            confidence_score=field_conf.overall,
            field_confidence=field_conf,
            status=status,
            debug_info=debug_info,
            success=not is_uncertain,
            error_message="Unable to reliably verify the current product price" if is_uncertain else None,
            product_url=url,
        )
