"""
Amazon Scraper Implementation
"""
import re
from typing import Optional
from bs4 import BeautifulSoup, Tag

from db.models import PlatformEnum, AvailabilityEnum
from scrapers.base import BaseScraper
from scrapers.shared.models import ExtractionResult, ExtractionDebug
from scrapers.shared.normalizers import SharedNormalizer
from scrapers.shared.confidence import ConfidenceEngine
from scrapers.amazon import selectors
from scrapers.amazon.extractors import AmazonExtractor
from scrapers.amazon.validators import AmazonValidator


class AmazonScraper(BaseScraper):
    store = PlatformEnum.amazon
    wait_selector = "#productTitle, #dp-container, #corePrice_desktop, #corePrice_feature_div"

    def extract_product_id(self, url: str) -> Optional[str]:
        """Extract Amazon 10-character ASIN."""
        if not url:
            return None
        patterns = [
            r'/(?:dp|product|gp/product|gp/aw/d|d)/([A-Z0-9]{10})',
            r'/([A-Z0-9]{10})(?:[/?]|$)',
            r'asin=([A-Z0-9]{10})',
        ]
        for pat in patterns:
            m = re.search(pat, url, re.IGNORECASE)
            if m:
                return m.group(1).upper()
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

        asin = self.extract_product_id(url)
        if not asin:
            can_link = soup.select_one("link[rel='canonical']")
            if can_link and can_link.get("href"):
                asin = self.extract_product_id(can_link["href"])
            if not asin:
                asin_inp = soup.select_one("input#ASIN, input[name='ASIN'], input[name='asin']")
                if asin_inp and asin_inp.get("value"):
                    asin = asin_inp["value"].strip()

        # 1. Title
        title = None
        for sel in selectors.TITLE_SELECTORS:
            elem = target.select_one(sel)
            if elem:
                title = SharedNormalizer.clean_title(elem.get_text())
                if title:
                    break

        if not title and soup.title:
            title = SharedNormalizer.clean_title(soup.title.string)

        # 2. Extract Candidates
        candidates, meta_data = AmazonExtractor.extract_candidates(soup, target)
        if not title and meta_data.get("json_ld_name"):
            title = SharedNormalizer.clean_title(meta_data["json_ld_name"])

        # 3. Price Ranking & Discount
        raw_price, raw_mrp = AmazonValidator.filter_and_rank_prices(candidates)

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

        # 4. Image, Brand, Rating & Variant
        image_url = AmazonExtractor.extract_image(target, soup) or meta_data.get("json_ld_image")
        brand = AmazonExtractor.extract_brand(target) or meta_data.get("json_ld_brand")
        # 4. Variant (Color/Size) & Variants Array
        variant = AmazonExtractor.extract_variant(target)
        variants = AmazonExtractor.extract_variants(
            soup=soup,
            target=target,
            default_price=current_price,
            default_mrp=original_price,
        )

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

        # 5. Availability (Scoped Buybox)
        avail_str, is_buybox_active = AmazonExtractor.extract_availability(target, soup)
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
            detected_store="amazon",
            extracted_product_id=asin,
            candidate_prices=[c.to_dict() for c in candidates],
            confidence_score=field_conf.overall,
            status=status,
        )

        return ExtractionResult(
            store=PlatformEnum.amazon,
            store_product_id=asin,
            title=title,
            brand=brand,
            current_price=current_price,
            original_price=original_price,
            discount_percentage=discount,
            saved_amount=saved_amount,
            image_url=image_url,
            rating=rating,
            rating_count=rating_count,
            review_count=meta_data.get("review_count"),
            currency="INR",
            availability=availability,
            variant=variant,
            variants=variants,
            canonical_url=f"https://www.amazon.in/dp/{asin}" if asin else url,
            confidence_score=field_conf.overall,
            field_confidence=field_conf,
            status=status,
            debug_info=debug_info,
            success=not is_uncertain,
            error_message="Unable to reliably verify the current product price" if is_uncertain else None,
            product_url=url,
        )
