"""
Candidate Price Extractor and Classifier
========================================
Collects all candidate prices from multiple page layers, classifies them by context (current price, MRP, coupon, bank offer, EMI, exchange, delivery, related product), and filters out non-product amounts.
"""
import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from bs4 import BeautifulSoup, Tag
from db.models import PlatformEnum
from scrapers.normalizers.price_normalizer import PriceNormalizer

logger = logging.getLogger(__name__)


class PriceCandidate:
    def __init__(self, value: float, source: str, label: str, confidence_weight: int, metadata: Optional[Dict[str, Any]] = None):
        self.value = value
        self.source = source
        self.label = label  # 'current_price', 'mrp', 'coupon_discount', 'bank_offer', 'exchange_value', 'emi', 'delivery', 'related_product'
        self.confidence_weight = confidence_weight
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "source": self.source,
            "label": self.label,
            "confidence_weight": self.confidence_weight,
            "metadata": self.metadata,
        }


class PriceExtractor:
    @classmethod
    def classify_price_context(cls, element: Tag, parent_text: str = "") -> Tuple[str, int]:
        """
        Classify the semantic context of a price element.
        Returns: (label: str, confidence_weight: int)
        """
        classes = " ".join(element.get("class", [])) if element else ""
        elem_id = element.get("id", "") if element else ""
        combined_text = (element.get_text() + " " + parent_text).lower() if element else parent_text.lower()

        # 1. Reject Coupon discounts
        if any(k in combined_text for k in ["coupon", "save with coupon", "apply coupon", "voucher"]):
            return "coupon_discount", -80

        # 2. Reject Bank offers & cashback
        if any(k in combined_text for k in ["bank offer", "instant discount", "cashback", "hdfc", "icici", "sbi", "axis", "credit card"]):
            return "bank_offer", -80

        # 3. Reject Exchange value
        if any(k in combined_text for k in ["exchange", "off on exchange", "with exchange", "trade in"]):
            return "exchange_value", -80

        # 4. Reject EMI amount
        if any(k in combined_text for k in ["emi", "per month", "/month", "/mo", "no cost emi"]):
            return "emi", -80

        # 5. Reject Delivery fee
        if any(k in combined_text for k in ["delivery", "shipping fee", "delivery charge"]):
            return "delivery", -80

        # 6. Reject Related / Recommended product section
        if any(k in combined_text for k in ["similar products", "customers who bought", "recommended", "sponsored", "carousel"]):
            return "related_product", -100

        # 7. Check for MRP / Strikethrough / List Price
        if any(k in classes.lower() for k in ["a-text-price", "a-text-strike", "strike", "mrp", "yray8j", "prod-cp", "css-u05rr", "pdp-mrp"]):
            return "mrp", 30

        # 8. Primary Current Price Selectors
        if any(k in classes.lower() for k in ["nx9bqj", "pdp-price", "prod-sp", "css-1jczs19", "apexprice", "a-price"]):
            return "current_price", 40

        return "current_price", 25

    @classmethod
    def extract_candidates(
        cls,
        soup: BeautifulSoup,
        container: Optional[Tag],
        platform: PlatformEnum,
        json_ld_data: Optional[Dict[str, Any]] = None,
        meta_data: Optional[Dict[str, Any]] = None,
    ) -> List[PriceCandidate]:
        """
        Extract and classify all candidate prices across DOM, JSON-LD, and metadata.
        """
        candidates: List[PriceCandidate] = []
        target_container = container or soup

        # 1. Extract JSON-LD price
        if json_ld_data and json_ld_data.get("current_price"):
            candidates.append(PriceCandidate(
                value=json_ld_data["current_price"],
                source="json_ld_offers",
                label="current_price",
                confidence_weight=35
            ))
        if json_ld_data and json_ld_data.get("original_price"):
            candidates.append(PriceCandidate(
                value=json_ld_data["original_price"],
                source="json_ld_high_price",
                label="mrp",
                confidence_weight=30
            ))

        # 2. Extract OpenGraph meta price
        if meta_data and meta_data.get("price"):
            candidates.append(PriceCandidate(
                value=meta_data["price"],
                source="meta_og_price",
                label="current_price",
                confidence_weight=20
            ))

        # 3. Platform-specific DOM price extraction
        if platform == PlatformEnum.amazon:
            cls._extract_amazon_candidates(target_container, soup, candidates)
        elif platform == PlatformEnum.flipkart:
            cls._extract_flipkart_candidates(target_container, soup, candidates)
        elif platform == PlatformEnum.myntra:
            cls._extract_myntra_candidates(target_container, soup, candidates)
        elif platform == PlatformEnum.ajio:
            cls._extract_ajio_candidates(target_container, soup, candidates)
        elif platform == PlatformEnum.nykaa:
            cls._extract_nykaa_candidates(target_container, soup, candidates)

        return candidates

    @classmethod
    def _extract_amazon_candidates(cls, container: Tag, soup: BeautifulSoup, candidates: List[PriceCandidate]):
        # MRP
        mrp_elem = container.select_one('.a-price.a-text-price .a-offscreen, span.basisPrice .a-offscreen')
        if mrp_elem:
            p = PriceNormalizer.clean_price(mrp_elem.get_text())
            if p:
                candidates.append(PriceCandidate(p, "amazon_mrp_strikethrough", "mrp", 35))

        # Selling price
        price_tags = [
            ("#corePrice_desktop .a-price:not(.a-text-price) .a-offscreen", "amazon_corePrice_desktop", 45),
            ("#corePrice_feature_div .a-price:not(.a-text-price) .a-offscreen", "amazon_corePrice_feature", 45),
            (".a-price:not(.a-text-price) .a-offscreen", "amazon_apex_price", 40),
            ("#priceblock_ourprice", "amazon_priceblock_ourprice", 40),
            ("#priceblock_dealprice", "amazon_priceblock_dealprice", 40),
        ]
        for sel, src, weight in price_tags:
            elem = container.select_one(sel) or soup.select_one(sel)
            if elem:
                p = PriceNormalizer.clean_price(elem.get_text())
                if p:
                    candidates.append(PriceCandidate(p, src, "current_price", weight))
                    break

    @classmethod
    def _extract_flipkart_candidates(cls, container: Tag, soup: BeautifulSoup, candidates: List[PriceCandidate]):
        # MRP
        mrp_elem = container.select_one('div.yRaY8j, div._3I9_wc._2p6lqe, span.yRaY8j') or soup.select_one('div.yRaY8j, div._3I9_wc._2p6lqe')
        if mrp_elem:
            p = PriceNormalizer.clean_price(mrp_elem.get_text())
            if p:
                candidates.append(PriceCandidate(p, "flipkart_mrp_dom", "mrp", 35))

        # Selling price
        price_elem = container.select_one('div.Nx9bqj.CxhGGd, div.Nx9bqj, div._30jeq3._16Jk6d, div._30jeq3') or soup.select_one('div.Nx9bqj.CxhGGd, div.Nx9bqj')
        if price_elem:
            p = PriceNormalizer.clean_price(price_elem.get_text())
            if p:
                candidates.append(PriceCandidate(p, "flipkart_current_price_dom", "current_price", 45))

    @classmethod
    def _extract_myntra_candidates(cls, container: Tag, soup: BeautifulSoup, candidates: List[PriceCandidate]):
        mrp_elem = container.select_one('span.pdp-mrp') or soup.select_one('span.pdp-mrp')
        if mrp_elem:
            p = PriceNormalizer.clean_price(mrp_elem.get_text())
            if p:
                candidates.append(PriceCandidate(p, "myntra_mrp_dom", "mrp", 35))

        price_elem = container.select_one('span.pdp-price, strong.pdp-price') or soup.select_one('span.pdp-price, strong.pdp-price')
        if price_elem:
            p = PriceNormalizer.clean_price(price_elem.get_text())
            if p:
                candidates.append(PriceCandidate(p, "myntra_current_price_dom", "current_price", 45))

    @classmethod
    def _extract_ajio_candidates(cls, container: Tag, soup: BeautifulSoup, candidates: List[PriceCandidate]):
        mrp_elem = container.select_one('.prod-cp, .prod-mrp, span[class*="mrp"], span[class*="prod-cp"]') or soup.select_one('.prod-cp, .prod-mrp')
        if mrp_elem:
            p = PriceNormalizer.clean_price(mrp_elem.get_text())
            if p:
                candidates.append(PriceCandidate(p, "ajio_mrp_dom", "mrp", 35))

        price_elem = container.select_one('.prod-sp, .prod-discounted-price, span[class*="prod-sp"], .price-value') or soup.select_one('.prod-sp, .price-value')
        if price_elem:
            p = PriceNormalizer.clean_price(price_elem.get_text())
            if p:
                candidates.append(PriceCandidate(p, "ajio_current_price_dom", "current_price", 45))

        # Check window.__PRELOADED_STATE__
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
                                p_obj = pd.get("price")
                                p_val = p_obj.get("value") if isinstance(p_obj, dict) else p_obj
                                if p_val:
                                    cp = PriceNormalizer.clean_price(p_val)
                                    if cp:
                                        candidates.append(PriceCandidate(cp, "ajio_preloaded_price", "current_price", 50))
                                w_obj = pd.get("wasPriceData")
                                w_val = w_obj.get("value") if isinstance(w_obj, dict) else w_obj
                                if w_val:
                                    wp = PriceNormalizer.clean_price(w_val)
                                    if wp:
                                        candidates.append(PriceCandidate(wp, "ajio_preloaded_mrp", "mrp", 40))
                except Exception:
                    pass
                break

    @classmethod
    def _extract_nykaa_candidates(cls, container: Tag, soup: BeautifulSoup, candidates: List[PriceCandidate]):
        mrp_elem = container.select_one('.css-u05rr, .mrp-price, span.css-17x46n5') or soup.select_one('.css-u05rr, .mrp-price')
        if mrp_elem:
            p = PriceNormalizer.clean_price(mrp_elem.get_text())
            if p:
                candidates.append(PriceCandidate(p, "nykaa_mrp_dom", "mrp", 35))

        price_elem = container.select_one('.css-1jczs19, .product-price-primary') or soup.select_one('.css-1jczs19')
        if price_elem:
            p = PriceNormalizer.clean_price(price_elem.get_text())
            if p:
                candidates.append(PriceCandidate(p, "nykaa_current_price_dom", "current_price", 45))
