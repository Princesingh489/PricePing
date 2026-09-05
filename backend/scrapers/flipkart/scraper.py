"""
Flipkart Scraper Implementation
"""
import re
from typing import Optional
from bs4 import BeautifulSoup, Tag

from db.models import PlatformEnum, AvailabilityEnum
from scrapers.base import BaseScraper
from scrapers.shared.models import ExtractionResult, ExtractionDebug
from scrapers.shared.normalizers import SharedNormalizer
from scrapers.shared.confidence import ConfidenceEngine
from scrapers.flipkart import selectors
from scrapers.flipkart.extractors import FlipkartExtractor
from scrapers.flipkart.validators import FlipkartValidator


class FlipkartScraper(BaseScraper):
    store = PlatformEnum.flipkart
    wait_selector = "span.VU-ZEz, h1.yhB1nd, div.Nx9bqj, div.DOjaWF"

    normalize_flipkart_image = staticmethod(FlipkartExtractor.normalize_flipkart_image)
    extract_largest_from_srcset = staticmethod(FlipkartExtractor.extract_largest_from_srcset)

    def extract_product_id(self, url: str) -> Optional[str]:
        """Extract Flipkart PID or item ID."""
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
        for sel in selectors.MAIN_CONTAINER_SELECTORS:
            elem = soup.select_one(sel)
            if elem:
                return elem
        return None

    def extract_from_html(self, html: str, url: str) -> ExtractionResult:
        soup = BeautifulSoup(html, "lxml")
        container = self.get_main_container(soup)
        target = container or soup

        pid = self.extract_product_id(url)
        if not pid:
            can_link = soup.select_one("link[rel='canonical']")
            if can_link and can_link.get("href"):
                pid = self.extract_product_id(can_link["href"])

        # 1. Variant Detection
        variant = FlipkartExtractor.extract_variant(soup, target, url)

        # 2. Title
        title = None
        for sel in selectors.TITLE_SELECTORS:
            elem = target.select_one(sel)
            if elem:
                title = SharedNormalizer.clean_title(elem.get_text())
                if title:
                    break

        if not title and soup.title:
            title = SharedNormalizer.clean_title(soup.title.string)

        # 3. Extract Candidates & Metadata
        candidates, meta_data = FlipkartExtractor.extract_candidates(soup, target)
        if not title and meta_data.get("json_ld_name"):
            title = SharedNormalizer.clean_title(meta_data["json_ld_name"])

        # 4. Brand & Title Cleanup
        brand = FlipkartExtractor.extract_brand(target) or meta_data.get("json_ld_brand")
        if title:
            # Remove consecutive duplicate words e.g. "KILLER Killer"
            title = re.sub(r'\b([A-Za-z0-9]+)\b\s+\1\b', r'\1', title, flags=re.IGNORECASE)
            if brand:
                escaped_brand = re.escape(brand.strip())
                title = re.sub(rf'^({escaped_brand}\s+)+', f'{brand.strip()} ', title, flags=re.IGNORECASE).strip()

        # 5. Discount & Price Ranking
        extracted_discount = meta_data.get("extracted_discount")
        if extracted_discount is None:
            for sel in selectors.DISCOUNT_SELECTORS:
                elem = target.select_one(sel) or soup.select_one(sel)
                if elem:
                    d_match = re.search(r'(\d+)', elem.get_text())
                    if d_match:
                        extracted_discount = float(d_match.group(1))
                        break

        raw_price, raw_mrp = FlipkartValidator.filter_and_rank_prices(
            candidates, extracted_discount=extracted_discount
        )

        current_price, original_price, discount, saved_amount = ConfidenceEngine.validate_and_calculate_discount(
            raw_price, raw_mrp, extracted_discount
        )

        # 6. Images, Colors, Rating
        gallery_images = FlipkartExtractor.extract_gallery_images(soup, target)
        image_url = FlipkartExtractor.extract_image(target, soup) or meta_data.get("json_ld_image")
        if not image_url and gallery_images:
            image_url = gallery_images[0]
        elif image_url and image_url not in gallery_images:
            gallery_images.insert(0, image_url)

        colors = FlipkartExtractor.extract_colors(soup, target)

        rating = meta_data.get("rating")
        if rating is None:
            for sel in selectors.RATING_SELECTORS:
                elem = target.select_one(sel)
                if elem:
                    rating = SharedNormalizer.parse_rating(elem.get_text())
                    if rating is not None:
                        break

        rating_count = meta_data.get("rating_count")
        review_count = meta_data.get("review_count")
        if rating_count is None:
            for sel in selectors.COUNT_SELECTORS:
                elem = target.select_one(sel)
                if elem:
                    text = elem.get_text()
                    m = re.search(r'([\d,]+(?:\.\d+)?\s*(?:lakh|k)?)\s*Ratings?', text, re.IGNORECASE)
                    if m:
                        rating_count = SharedNormalizer.parse_count(m.group(1))
                    r_m = re.search(r'([\d,]+(?:\.\d+)?\s*(?:lakh|k)?)\s*Reviews?', text, re.IGNORECASE)
                    if r_m:
                        review_count = SharedNormalizer.parse_count(r_m.group(1))
                    if rating_count is not None:
                        break

        # 7. Scoped Buybox Availability & Variants
        variants = FlipkartExtractor.extract_variants(
            soup=soup,
            target=target,
            default_price=current_price,
            default_mrp=original_price,
        )
        availability, is_buybox_active = FlipkartExtractor.extract_availability(soup, target)

        # 8. Confidence Scoring
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
            detected_store="flipkart",
            extracted_product_id=pid,
            candidate_prices=[c.to_dict() for c in candidates],
            confidence_score=field_conf.overall,
            status=status,
        )

        return ExtractionResult(
            store=PlatformEnum.flipkart,
            store_product_id=pid,
            title=title,
            brand=brand,
            current_price=current_price,
            original_price=original_price,
            discount_percentage=discount,
            saved_amount=saved_amount,
            image_url=image_url,
            images=gallery_images,
            colors=colors,
            rating=rating,
            rating_count=rating_count,
            review_count=review_count,
            currency="INR",
            availability=availability,
            variant=variant or None,
            variants=variants,
            canonical_url=url,
            confidence_score=field_conf.overall,
            field_confidence=field_conf,
            status=status,
            debug_info=debug_info,
            success=not is_uncertain,
            error_message="Unable to reliably verify the current product price" if is_uncertain else None,
            product_url=url,
        )
