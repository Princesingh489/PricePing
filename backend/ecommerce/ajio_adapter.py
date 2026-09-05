"""
AJIO Ecommerce Adapter
======================
Modular adapter for AJIO (Reliance Retail). Handles URL detection, product code extraction,
product fetching, price observation, and cross-store search.
"""

import re
import urllib.parse
import logging
from typing import Optional, Dict, Any, List

from ecommerce.base_adapter import BaseEcommerceAdapter
from ecommerce.product_matcher import is_strict_match
from scrapers.ajio.scraper import AjioScraper
from scrapers.shared.models import ExtractionResult

logger = logging.getLogger(__name__)


class AjioAdapter(BaseEcommerceAdapter):
    store_name = "ajio"
    display_name = "AJIO"
    logo_icon = "ajio"

    def __init__(self):
        self._scraper = AjioScraper()

    def detect_url(self, url: str) -> bool:
        if not url:
            return False
        u = url.lower()
        return "ajio.com" in u or "ajio.in" in u or "ajio.page.link" in u

    def extract_product_id(self, url: str) -> Optional[str]:
        return self._scraper.extract_product_id(url)

    async def fetch_product(self, url: str) -> Optional[Dict[str, Any]]:
        result: ExtractionResult = await self._scraper.extract_product(url)
        if not result or not result.success:
            return None

        pid = result.store_product_id or self.extract_product_id(url)
        images = [result.image_url] if result.image_url else []

        return {
            "store": self.store_name,
            "product_id": pid,
            "title": result.title or "",
            "price": result.current_price,
            "original_price": result.original_price,
            "discount_percentage": result.discount_percentage,
            "currency": result.currency or "INR",
            "availability": result.availability.value if hasattr(result.availability, "value") else str(result.availability),
            "image_url": result.image_url,
            "images": images,
            "rating": result.rating,
            "rating_count": result.rating_count,
            "review_count": result.review_count,
            "brand": getattr(result, "brand", None),
            "seller": "AJIO Reliance Retail",
            "url": url,
        }

    async def fetch_current_price(self, url: str) -> Optional[float]:
        prod = await self.fetch_product(url)
        return prod["price"] if prod else None

    async def search_matching_product(
        self,
        title: str,
        brand: Optional[str] = None,
        model: Optional[str] = None,
        variant: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Search AJIO for matching product with strict variant verification.
        """
        try:
            from ecommerce.product_matcher import extract_specs, normalize_size
            base_specs = extract_specs(title, brand=brand)
            b_brand = base_specs.get("brand") or brand or ""
            b_model = base_specs.get("model") or model or ""
            b_size = base_specs.get("size") or variant or ""

            if b_brand and b_model:
                query = f"{b_brand} {b_model}"
                if b_size:
                    query += f" {b_size}"
            else:
                words = [w for w in re.sub(r'[^\w\s]', ' ', title).split() if w and not w.startswith(('http', 'www'))]
                query = " ".join(words[:6]) or title
            encoded = urllib.parse.quote_plus(query[:80])
            search_url = f"https://www.ajio.com/search/?text={encoded}"

            html = await self._scraper.fetch_fast_http(search_url)
            if not html:
                return None

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "lxml")

            best_score = 0.0
            best_reason = "No matching search results"
            best_signals = None

            items = soup.select("div.item, div.rilrtl-products-list__item")
            for item in items[:6]:
                brand_elem = item.select_one("div.brand")
                name_elem = item.select_one("div.name")
                cand_brand = brand_elem.get_text(strip=True) if brand_elem else ""
                cand_name = name_elem.get_text(strip=True) if name_elem else ""
                cand_title = f"{cand_brand} {cand_name}".strip()

                if not cand_title:
                    continue

                res = is_strict_match(
                    base_title=title,
                    candidate_title=cand_title,
                    base_brand=brand or cand_brand,
                )
                if not res.is_match:
                    if res.confidence > best_score:
                        best_score = res.confidence
                        best_reason = res.reason
                        best_signals = getattr(res, "signals", None)
                    continue

                # Price
                price_elem = item.select_one("span.price")
                clean_p = re.sub(r"[^\d]", "", price_elem.get_text()) if price_elem else ""
                cand_price = float(clean_p) if clean_p else None

                # Strike MRP
                mrp_elem = item.select_one("span.orginal-price")
                cand_mrp = None
                if mrp_elem:
                    clean_m = re.sub(r"[^\d]", "", mrp_elem.get_text())
                    if clean_m:
                        cand_mrp = float(clean_m)

                link_elem = item.select_one("a[href]")
                href = link_elem.get("href") if link_elem else None
                cand_url = f"https://www.ajio.com{href}" if href and href.startswith("/") else (href or search_url)
                pid = self.extract_product_id(cand_url)

                cand_specs = extract_specs(cand_title, brand=brand or cand_brand)
                c_size = cand_specs.get("size")
                variants_list = []

                # Size verification rule
                if b_size:
                    if c_size and normalize_size(c_size) != normalize_size(b_size):
                        continue
                    if not c_size:
                        try:
                            cand_prod = await self._scraper.extract_product(cand_url)
                            if cand_prod.success and cand_prod.variants:
                                variants_list = cand_prod.variants
                                matched_sz = next((v for v in cand_prod.variants if normalize_size(v.get("size")) == normalize_size(b_size)), None)
                                if matched_sz:
                                    cand_price = float(matched_sz.get("price") or cand_price or 0.0)
                                    cand_mrp = float(matched_sz.get("mrp") or cand_mrp or cand_price)
                                else:
                                    continue
                            elif cand_prod.success and cand_prod.current_price is not None:
                                cand_price = cand_prod.current_price
                                cand_mrp = cand_prod.original_price
                        except Exception:
                            pass

                if cand_price is None:
                    continue

                if not variants_list:
                    variants_list = [{"size": b_size or "Standard", "price": cand_price, "mrp": cand_mrp, "in_stock": True, "sku": pid}]

                return {
                    "store": self.store_name,
                    "seller_name": "AJIO Official Store",
                    "seller_id": pid or "ajio_seller",
                    "price": cand_price,
                    "original_price": cand_mrp,
                    "shipping_price": 0.0,
                    "delivery_text": "Free Delivery (Orders > ₹999)",
                    "coupon_text": "Apply Coupon AJIOMANIA for extra off",
                    "url": cand_url,
                    "availability": "in_stock",
                    "external_product_id": pid,
                    "is_verified_match": True,
                    "status": "available",
                    "match_confidence": res.confidence,
                    "match_signals": getattr(res, "signals", None),
                    "match_reason": res.reason,
                    "variants": variants_list,
                }

            # Return explicit non-match
            return {
                "store": self.store_name,
                "seller_name": "AJIO",
                "seller_id": None,
                "price": None,
                "original_price": None,
                "shipping_price": 0.0,
                "delivery_text": "Not Available",
                "coupon_text": None,
                "url": search_url,
                "availability": "unavailable",
                "external_product_id": None,
                "is_verified_match": False,
                "status": "no_match",
                "match_confidence": best_score,
                "match_signals": best_signals,
                "match_reason": f"No exact match found on AJIO ({best_reason})",
                "variants": [],
            }
        except Exception as e:
            logger.debug(f"AJIO matching search error: {e}")
        return None
