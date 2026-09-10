"""
Myntra Extractors
"""
import re
import json
import logging
from typing import Optional, Dict, Any, List, Tuple
from bs4 import BeautifulSoup, Tag

from scrapers.shared.models import PriceCandidate
from scrapers.shared.normalizers import SharedNormalizer
from scrapers.myntra import selectors

logger = logging.getLogger(__name__)


class MyntraExtractor:
    @classmethod
    def _parse_myx_data(cls, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Safely parse window.__myx script data containing complete official PDP JSON."""
        for script in soup.find_all("script"):
            txt = script.string or script.get_text() or ""
            if "window.__myx" in txt or "pdpData" in txt:
                try:
                    idx = txt.find("window.__myx =")
                    if idx != -1:
                        sub = txt[idx + len("window.__myx ="):].strip()
                        data, _ = json.JSONDecoder().raw_decode(sub)
                        pdp = data.get("pdpData", data)
                        if pdp:
                            return pdp
                except Exception:
                    pass
        return None

    @classmethod
    def extract_candidates(cls, soup: BeautifulSoup, target: Tag | BeautifulSoup) -> Tuple[List[PriceCandidate], Dict[str, Any]]:
        candidates: List[PriceCandidate] = []
        meta_data: Dict[str, Any] = {}

        # 0. window.__myx official PDP Data (Fastest, 100% verified ground truth)
        pdp = cls._parse_myx_data(soup)
        if pdp:
            p_name = pdp.get("name")
            if p_name:
                meta_data["json_ld_name"] = p_name
            brand_obj = pdp.get("brand", {})
            b_name = brand_obj.get("name") if isinstance(brand_obj, dict) else str(brand_obj or "")
            if b_name:
                meta_data["json_ld_brand"] = b_name
            price_obj = pdp.get("price", {})
            if isinstance(price_obj, dict):
                disc_price = price_obj.get("discounted")
                mrp_price = price_obj.get("mrp")
                if disc_price and float(disc_price) > 0:
                    candidates.append(PriceCandidate(
                        value=float(disc_price),
                        source="myntra_myx_discounted",
                        category="selling_price",
                        confidence=99,
                        raw_text=str(disc_price)
                    ))
                if mrp_price and float(mrp_price) > 0:
                    candidates.append(PriceCandidate(
                        value=float(mrp_price),
                        source="myntra_myx_mrp",
                        category="mrp",
                        confidence=99,
                        raw_text=str(mrp_price)
                    ))
            ratings_obj = pdp.get("ratings", {})
            if isinstance(ratings_obj, dict):
                if ratings_obj.get("averageRating"):
                    meta_data["rating"] = round(float(ratings_obj["averageRating"]), 1)
                if ratings_obj.get("totalCount"):
                    meta_data["rating_count"] = int(ratings_obj["totalCount"])

        # 1. JSON-LD
        for script in soup.select('script[type="application/ld+json"]'):
            try:
                data = json.loads(script.string or "{}")
                if isinstance(data, list):
                    data = data[0] if data else {}
                if data.get("@type") == "Product":
                    if not meta_data.get("json_ld_name"):
                        meta_data["json_ld_name"] = data.get("name")
                    meta_data["json_ld_image"] = data.get("image")
                    if not meta_data.get("json_ld_brand"):
                        meta_data["json_ld_brand"] = data.get("brand", {}).get("name") if isinstance(data.get("brand"), dict) else data.get("brand")
                    offers = data.get("offers", {})
                    if isinstance(offers, list):
                        offers = offers[0] if offers else {}
                    if offers.get("price"):
                        val = SharedNormalizer.clean_price(offers["price"])
                        if val:
                            candidates.append(PriceCandidate(value=val, source="myntra_json_ld_offer", category="selling_price", confidence=95))
                    if offers.get("highPrice"):
                        mrp_val = SharedNormalizer.clean_price(offers["highPrice"])
                        if mrp_val:
                            candidates.append(PriceCandidate(value=mrp_val, source="myntra_json_ld_mrp", category="mrp", confidence=90))
                    agg = data.get("aggregateRating", {})
                    if agg:
                        if meta_data.get("rating") is None:
                            meta_data["rating"] = SharedNormalizer.parse_rating(agg.get("ratingValue"))
                        if meta_data.get("rating_count") is None:
                            meta_data["rating_count"] = SharedNormalizer.parse_count(agg.get("ratingCount"))
            except Exception:
                pass

        # 2. Visible selling price
        for sel in selectors.PRICE_SELECTORS:
            for elem in target.select(sel):
                val = SharedNormalizer.clean_price(elem.get_text())
                if val and val > 0:
                    candidates.append(PriceCandidate(value=val, source=f"myntra_{sel}", category="selling_price", confidence=95, raw_text=elem.get_text()))

        # 3. MRP
        for sel in selectors.MRP_SELECTORS:
            for elem in target.select(sel):
                val = SharedNormalizer.clean_price(elem.get_text())
                if val and val > 0:
                    candidates.append(PriceCandidate(value=val, source=f"myntra_mrp_{sel}", category="mrp", confidence=90, raw_text=elem.get_text()))

        return candidates, meta_data

    @classmethod
    def extract_image(cls, target: Tag | BeautifulSoup, soup: BeautifulSoup) -> Optional[str]:
        # 1. Parse window.__myx media albums (highest resolution official product images)
        for script in soup.find_all("script"):
            txt = script.string or script.get_text() or ""
            if "window.__myx" in txt or "pdpData" in txt:
                try:
                    idx = txt.find("window.__myx =")
                    if idx != -1:
                        sub = txt[idx + len("window.__myx ="):].strip()
                        data, _ = json.JSONDecoder().raw_decode(sub)
                        pdp = data.get("pdpData", {})
                        media = pdp.get("media", {})
                        for alb in media.get("albums", []):
                            for im in alb.get("images", []):
                                src = im.get("secureSrc") or im.get("src") or im.get("imageURL")
                                if src:
                                    src = src.replace("($height)", "720").replace("($width)", "540").replace("($qualityPercentage)", "90")
                                    if src.startswith("http://"):
                                        src = "https://" + src[7:]
                                    if not any(bad in src.lower() for bad in ["logo", "studio-logo", "icon", "banner", ".svg"]):
                                        return src
                except Exception:
                    pass

        # 2. JSON-LD Image
        for script in soup.select('script[type="application/ld+json"]'):
            try:
                data = json.loads(script.string or "{}")
                if isinstance(data, list):
                    data = data[0] if data else {}
                img = data.get("image")
                if isinstance(img, list) and img:
                    img = img[0]
                if img and isinstance(img, str) and not any(bad in img.lower() for bad in ["logo", "studio-logo", "icon", "banner", ".svg"]):
                    return img.strip()
            except Exception:
                pass

        # 3. DOM Image Selectors
        for sel in selectors.IMAGE_SELECTORS:
            elements = target.select(sel)
            if not elements:
                elements = soup.select(sel)
            for elem in elements:
                src = elem.get("src") or elem.get("data-src")
                if src and "http" in src and not any(bad in src.lower() for bad in ["logo", "studio-logo", "icon", "banner", ".svg"]):
                    return src

        # 4. OpenGraph Image
        og_img = soup.select_one("meta[property='og:image']")
        if og_img and og_img.get("content"):
            c = og_img["content"].strip()
            if not any(bad in c.lower() for bad in ["logo", "studio-logo", "icon", "banner", ".svg"]):
                return c
        return None

    @classmethod
    def extract_images(cls, soup: BeautifulSoup) -> List[str]:
        images: List[str] = []
        for script in soup.find_all("script"):
            txt = script.string or script.get_text() or ""
            if "window.__myx" in txt or "pdpData" in txt:
                try:
                    idx = txt.find("window.__myx =")
                    if idx != -1:
                        sub = txt[idx + len("window.__myx ="):].strip()
                        data, _ = json.JSONDecoder().raw_decode(sub)
                        pdp = data.get("pdpData", {})
                        media = pdp.get("media", {})
                        for alb in media.get("albums", []):
                            for im in alb.get("images", []):
                                src = im.get("secureSrc") or im.get("src") or im.get("imageURL")
                                if src:
                                    src = src.replace("($height)", "720").replace("($width)", "540").replace("($qualityPercentage)", "90")
                                    if src.startswith("http://"):
                                        src = "https://" + src[7:]
                                    if not any(bad in src.lower() for bad in ["logo", "studio-logo", "icon", "banner", ".svg"]):
                                        if src not in images:
                                            images.append(src)
                except Exception:
                    pass
        return images

    @classmethod
    def extract_brand(cls, target: Tag | BeautifulSoup) -> Optional[str]:
        for sel in selectors.BRAND_SELECTORS:
            elem = target.select_one(sel)
            if elem:
                text = elem.get_text().strip()
                if len(text) >= 2:
                    return text
        return None

    @classmethod
    def extract_variant(cls, soup: BeautifulSoup, target: Tag | BeautifulSoup, url: str) -> Optional[Dict[str, str]]:
        variant = {}
        for sel in selectors.ACTIVE_SIZE_SELECTORS:
            elem = target.select_one(sel) or soup.select_one(sel)
            if elem:
                txt = elem.get_text().strip()
                if txt and len(txt) <= 10:
                    variant["size"] = txt
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
        seen_sizes = set()

        # 1. Parse window.__myx script object if present
        pdp_data = cls._parse_myx_data(soup)
        if pdp_data:
            sizes = pdp_data.get("sizes") or pdp_data.get("style", {}).get("sizes", [])
            for s_info in sizes:
                label = str(s_info.get("label") or s_info.get("name") or "").strip()
                if not label or label.lower() in seen_sizes:
                    continue
                seen_sizes.add(label.lower())
                price_obj = s_info.get("price") or {}
                if isinstance(price_obj, dict):
                    v_price = float(price_obj.get("discounted") or price_obj.get("sellingPrice") or default_price or 0.0)
                    v_mrp = float(price_obj.get("mrp") or default_mrp or v_price)
                else:
                    v_price = float(s_info.get("discountedPrice") or default_price or 0.0)
                    v_mrp = float(s_info.get("mrp") or default_mrp or v_price)

                is_available = bool(s_info.get("available", True))
                if "inventory" in s_info:
                    is_available = is_available and (s_info.get("inventory", 1) > 0)

                variants.append({
                    "size": label,
                    "price": v_price if v_price > 0 else (default_price or 0.0),
                    "mrp": v_mrp if v_mrp > 0 else default_mrp,
                    "in_stock": is_available,
                    "sku": str(s_info.get("skuId") or ""),
                })

        # 2. DOM fallback: Size buttons
        if not variants:
            size_buttons = target.select("button.size-buttons-size-button, div.size-buttons-tipAndBtnContainer button, button[class*='size-button']")
            if not size_buttons:
                size_buttons = soup.select("button.size-buttons-size-button, div.size-buttons-tipAndBtnContainer button, button[class*='size-button']")

            for btn in size_buttons:
                txt = btn.get_text(strip=True)
                cleaned_label = re.sub(r'(?:few left|left|selling fast).*', '', txt, flags=re.IGNORECASE).strip()
                if not cleaned_label or len(cleaned_label) > 15:
                    continue
                if cleaned_label.lower() in seen_sizes:
                    continue
                seen_sizes.add(cleaned_label.lower())

                btn_classes = " ".join(btn.get("class", []))
                in_stock = not ("disabled" in btn_classes or "size-buttons-size-button-disabled" in btn_classes)
                btn_p = SharedNormalizer.clean_price(btn.get_text()) or default_price or 0.0

                variants.append({
                    "size": cleaned_label,
                    "price": float(btn_p),
                    "mrp": default_mrp,
                    "in_stock": in_stock,
                    "sku": btn.get("data-sku") or None,
                })

        return variants

    @classmethod
    def extract_availability(cls, soup: BeautifulSoup, target: Tag | BeautifulSoup) -> Tuple[Any, bool]:
        # Check active Add to Bag button
        for sel in selectors.BUYBOX_CART_BUTTONS:
            elem = target.select_one(sel) or soup.select_one(sel)
            if elem:
                return "in_stock", True

        for sel in selectors.BUYBOX_OUT_OF_STOCK_SELECTORS:
            elem = target.select_one(sel) or soup.select_one(sel)
            if elem:
                return "out_of_stock", False

        return "in_stock", True
