"""
Rating and Review Extractor
===========================
Extracts product star ratings (0.0 to 5.0) and separate rating counts and review counts.
"""
import re
from typing import Optional, Tuple, Dict, Any
from bs4 import BeautifulSoup, Tag
from db.models import PlatformEnum
from scrapers.normalizers.number_normalizer import NumberNormalizer


class RatingExtractor:
    @classmethod
    def extract_ratings_and_counts(
        cls,
        soup: BeautifulSoup,
        container: Optional[Tag],
        platform: PlatformEnum,
        json_ld_data: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Optional[float], Optional[int], Optional[int]]:
        """
        Extract: (rating, rating_count, review_count)
        """
        rating = None
        rating_count = None
        review_count = None
        target_container = container or soup

        # 1. Check visible DOM by platform
        if platform == PlatformEnum.amazon:
            r_elem = target_container.select_one(
                "#acrPopover span.a-size-base.a-color-base, "
                "#acrPopover i.a-icon-star span.a-icon-alt, "
                "span[data-hook='rating-out-of-text']"
            )
            if r_elem:
                rating = NumberNormalizer.parse_rating(r_elem.get_text())

            rc_elem = target_container.select_one("#acrCustomerReviewText, span[data-hook='total-review-count']")
            if rc_elem:
                rating_count = NumberNormalizer.parse_count(rc_elem.get_text())

        elif platform == PlatformEnum.flipkart:
            r_elem = target_container.select_one("div.XQDdHH, div._3LWZKl, span._1lRcqv div._3LWZKl, div._2d4LTz")
            if r_elem:
                rating = NumberNormalizer.parse_rating(r_elem.get_text())

            count_elem = target_container.select_one("span.WNMewY span, span._2_R_DZ span, span.WNMewY, span._2_R_DZ")
            if count_elem:
                raw_c = count_elem.get_text()
                m_rat = re.search(r'([\d,]+|\d+(?:\.\d+)?\s*(?:lakh|lac|k|m))\s*ratings?', raw_c, re.IGNORECASE)
                if m_rat:
                    rating_count = NumberNormalizer.parse_count(m_rat.group(1))

                m_rev = re.search(r'([\d,]+|\d+(?:\.\d+)?\s*(?:lakh|lac|k|m))\s*reviews?', raw_c, re.IGNORECASE)
                if m_rev:
                    review_count = NumberNormalizer.parse_count(m_rev.group(1))

        elif platform == PlatformEnum.myntra:
            r_elem = target_container.select_one("div.index-overallRating div, .index-overallRating, .pdp-ratings-container span")
            if r_elem:
                rating = NumberNormalizer.parse_rating(r_elem.get_text())

            rc_elem = target_container.select_one("div.index-ratingsCount, .pdp-ratings-count, div.index-countDesc")
            if rc_elem:
                rating_count = NumberNormalizer.parse_count(rc_elem.get_text())

        elif platform == PlatformEnum.ajio:
            r_elem = target_container.select_one(".prod-rating, span._3I-x0, .stars-rating")
            if r_elem:
                rating = NumberNormalizer.parse_rating(r_elem.get_text())

            rc_elem = target_container.select_one(".prod-rating-count, .rating-count")
            if rc_elem:
                rating_count = NumberNormalizer.parse_count(rc_elem.get_text())

        elif platform == PlatformEnum.nykaa:
            r_elem = target_container.select_one(".css-15pe18n, span.css-13bbf7w, .product-rating-value")
            if r_elem:
                rating = NumberNormalizer.parse_rating(r_elem.get_text())

            rc_elem = target_container.select_one("span.css-1n9y6j, span.css-19u0p98, .product-rating-count")
            if rc_elem:
                raw_c = rc_elem.get_text()
                rating_count = NumberNormalizer.parse_count(raw_c)

        # 2. JSON-LD Fallback
        if json_ld_data:
            if rating is None and json_ld_data.get("rating") is not None:
                rating = json_ld_data["rating"]
            if rating_count is None and json_ld_data.get("rating_count") is not None:
                rating_count = json_ld_data["rating_count"]
            if review_count is None and json_ld_data.get("review_count") is not None:
                review_count = json_ld_data["review_count"]

        return rating, rating_count, review_count
