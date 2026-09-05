"""
Nykaa Extractors
"""
import re
import json
import logging
from typing import Optional, Dict, Any, List, Tuple
from bs4 import BeautifulSoup, Tag

from scrapers.shared.models import PriceCandidate
from scrapers.shared.normalizers import SharedNormalizer
from scrapers.nykaa import selectors

logger = logging.getLogger(__name__)


class NykaaExtractor:
    @classmethod
    def extract_candidates(cls, soup: BeautifulSoup, target: Tag | BeautifulSoup) -> Tuple[List[PriceCandidate], Dict[str, Any]]:
        candidates: List[PriceCandidate] = []
        meta_data: Dict[str, Any] = {}

        # 1. JSON-LD
        for script in soup.select('script[type="application/ld+json"]'):
            try:
                data = json.loads(script.string or "{}")
                if isinstance(data, list):
                    data = data[0] if data else {}
                if data.get("@type") == "Product":
                    meta_data["json_ld_name"] = data.get("name")
                    meta_data["json_ld_image"] = data.get("image")
                    meta_data["json_ld_brand"] = data.get("brand", {}).get("name") if isinstance(data.get("brand"), dict) else data.get("brand")
                    offers = data.get("offers", {})
                    if isinstance(offers, list):
                        offers = offers[0] if offers else {}
                    if offers.get("price"):
                        val = SharedNormalizer.clean_price(offers["price"])
                        if val:
                            candidates.append(PriceCandidate(value=val, source="nykaa_json_ld_offer", category="selling_price", confidence=95))
                    if offers.get("highPrice"):
                        mrp_val = SharedNormalizer.clean_price(offers["highPrice"])
                        if mrp_val:
                            candidates.append(PriceCandidate(value=mrp_val, source="nykaa_json_ld_mrp", category="mrp", confidence=90))
                    agg = data.get("aggregateRating", {})
                    if agg:
                        meta_data["rating"] = SharedNormalizer.parse_rating(agg.get("ratingValue"))
                        meta_data["rating_count"] = SharedNormalizer.parse_count(agg.get("ratingCount"))
            except Exception:
                pass

        # 2. Visible price
        for sel in selectors.PRICE_SELECTORS:
            for elem in target.select(sel):
                val = SharedNormalizer.clean_price(elem.get_text())
                if val and val > 0:
                    candidates.append(PriceCandidate(value=val, source=f"nykaa_{sel}", category="selling_price", confidence=95, raw_text=elem.get_text()))

        # 3. MRP
        for sel in selectors.MRP_SELECTORS:
            for elem in target.select(sel):
                val = SharedNormalizer.clean_price(elem.get_text())
                if val and val > 0:
                    candidates.append(PriceCandidate(value=val, source=f"nykaa_mrp_{sel}", category="mrp", confidence=90, raw_text=elem.get_text()))

        return candidates, meta_data

    @classmethod
    def extract_image(cls, target: Tag | BeautifulSoup, soup: BeautifulSoup) -> Optional[str]:
        # 1. OpenGraph Image (Nykaa always puts high-res 800x800 product photo in og:image)
        og_img = soup.select_one("meta[property='og:image']")
        if og_img and og_img.get("content"):
            c = og_img["content"].strip()
            if not any(bad in c.lower() for bad in ["logo", "menu-logo", "uitools", "icon", "banner", ".svg"]):
                return c

        # 2. JSON-LD Image
        for script in soup.select('script[type="application/ld+json"]'):
            try:
                data = json.loads(script.string or "{}")
                items = data if isinstance(data, list) else [data]
                for it in items:
                    if it.get("@type") == "Product" and it.get("image"):
                        img = it["image"]
                        if isinstance(img, list) and img:
                            img = img[0]
                        if isinstance(img, str) and not any(bad in img.lower() for bad in ["logo", "menu-logo", "uitools", "icon", "banner", ".svg"]):
                            return img.strip()
            except Exception:
                pass

        # 3. DOM Image Selectors
        for sel in selectors.IMAGE_SELECTORS:
            for elem in target.select(sel):
                src = elem.get("src") or elem.get("data-src")
                if src and "http" in src and not any(bad in src.lower() for bad in ["logo", "menu-logo", "uitools", "icon", "banner", ".svg"]):
                    return src

        return None

    @classmethod
    def extract_images(cls, soup: BeautifulSoup) -> List[str]:
        images: List[str] = []
        for img in soup.select("img[src*='/media/catalog/product/']"):
            src = img.get("src") or img.get("data-src")
            if src and src.startswith("http") and not any(bad in src.lower() for bad in ["logo", "menu-logo", "uitools", "icon", ".svg"]):
                if src not in images:
                    images.append(src)
        return images

    @classmethod
    def extract_variant(cls, soup: BeautifulSoup, target: Tag | BeautifulSoup, url: str) -> Optional[Dict[str, str]]:
        variant = {}
        for sel in selectors.ACTIVE_SHADE_SELECTORS:
            elem = target.select_one(sel) or soup.select_one(sel)
            if elem:
                txt = elem.get_text().strip()
                if txt and len(txt) <= 25:
                    variant["shade"] = txt
                    break
        return variant or None

    @classmethod
    def extract_variants(
        cls,
        soup: BeautifulSoup,
        target: Tag | BeautifulSoup,
        default_price: Optional[float] = None,
        default_mrp: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        variants: List[Dict[str, Any]] = []
        seen_shades = set()

        # Look for shade/size cards
        shades = soup.select("div[class*='shade-card'], div[class*='shade-item'], button[class*='size-select'], div[class*='pack-size']")
        for s in shades:
            txt = s.get("title") or s.get_text(strip=True)
            cleaned = re.sub(r'[^a-zA-Z0-9\s-]', '', txt).strip()
            if not cleaned or len(cleaned) > 25:
                continue
            if cleaned.lower() in seen_shades:
                continue
            seen_shades.add(cleaned.lower())

            s_classes = " ".join(s.get("class", []))
            in_stock = not ("out-of-stock" in s_classes or "disabled" in s_classes)
            p_val = SharedNormalizer.clean_price(s.get_text()) or default_price or 0.0

            variants.append({
                "size": cleaned,
                "price": float(p_val),
                "mrp": default_mrp,
                "in_stock": in_stock,
                "sku": s.get("data-sku") or None,
            })

        return variants

    @classmethod
    def extract_availability(cls, soup: BeautifulSoup, target: Tag | BeautifulSoup) -> Tuple[Any, bool]:
        # Check active buybox button
        for sel in selectors.BUYBOX_CART_BUTTONS:
            elem = target.select_one(sel) or soup.select_one(sel)
            if elem:
                return "in_stock", True

        for sel in selectors.BUYBOX_OUT_OF_STOCK_SELECTORS:
            elem = target.select_one(sel) or soup.select_one(sel)
            if elem:
                return "out_of_stock", False

        return "in_stock", True
