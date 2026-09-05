"""
Amazon Extractors
"""
import re
import json
import logging
from typing import Optional, Dict, Any, List, Tuple
from bs4 import BeautifulSoup, Tag

from scrapers.shared.models import PriceCandidate
from scrapers.shared.normalizers import SharedNormalizer
from scrapers.amazon import selectors

logger = logging.getLogger(__name__)


class AmazonExtractor:
    @classmethod
    def extract_candidates(cls, soup: BeautifulSoup, target: Tag | BeautifulSoup) -> Tuple[List[PriceCandidate], Dict[str, Any]]:
        candidates: List[PriceCandidate] = []
        meta_data: Dict[str, Any] = {}

        # 1. JSON-LD extraction
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
                            candidates.append(PriceCandidate(value=val, source="amazon_json_ld_offer", category="selling_price", confidence=95))
                    agg = data.get("aggregateRating", {})
                    if agg:
                        meta_data["rating"] = SharedNormalizer.parse_rating(agg.get("ratingValue"))
                        meta_data["rating_count"] = SharedNormalizer.parse_count(agg.get("ratingCount"))
                        meta_data["review_count"] = SharedNormalizer.parse_count(agg.get("reviewCount"))
            except Exception:
                pass

        # 2. Visible Price candidates
        for sel in selectors.PRICE_SELECTORS:
            for elem in target.select(sel):
                val = SharedNormalizer.clean_price(elem.get_text())
                if val and val > 0:
                    candidates.append(PriceCandidate(value=val, source=f"amazon_{sel}", category="selling_price", confidence=90, raw_text=elem.get_text()))

        # 3. MRP strikethrough candidates
        for sel in selectors.MRP_SELECTORS:
            for elem in target.select(sel):
                val = SharedNormalizer.clean_price(elem.get_text())
                if val and val > 0:
                    candidates.append(PriceCandidate(value=val, source=f"amazon_mrp_{sel}", category="mrp", confidence=90, raw_text=elem.get_text()))

        return candidates, meta_data

    @classmethod
    def extract_image(cls, target: Tag | BeautifulSoup, soup: BeautifulSoup) -> Optional[str]:
        # Landing image dynamic hires
        img_elem = target.select_one("img#landingImage, img#imgBlkFront")
        if img_elem:
            dynamic_str = img_elem.get("data-a-dynamic-image")
            if dynamic_str:
                try:
                    dyn_map = json.loads(dynamic_str)
                    if isinstance(dyn_map, dict) and dyn_map:
                        # Largest resolution
                        best = sorted(dyn_map.items(), key=lambda x: x[1][0] * x[1][1] if isinstance(x[1], list) else 0, reverse=True)
                        return best[0][0]
                except Exception:
                    pass
            hires = img_elem.get("data-old-hires")
            if hires and "http" in hires:
                return hires
            src = img_elem.get("src")
            if src and "http" in src and not src.endswith(".gif"):
                return src

        # OpenGraph fallback
        og_img = soup.select_one("meta[property='og:image']")
        if og_img and og_img.get("content"):
            return og_img["content"].strip()
        return None

    @classmethod
    def extract_brand(cls, target: Tag | BeautifulSoup) -> Optional[str]:
        for sel in selectors.BRAND_SELECTORS:
            elem = target.select_one(sel)
            if elem:
                text = elem.get_text().strip()
                text = re.sub(r'^(?:Brand:|Visit the)\s*', '', text, flags=re.IGNORECASE).strip()
                text = re.sub(r'\s*Store$', '', text, flags=re.IGNORECASE).strip()
                if len(text) >= 2:
                    return text
        return None

    @classmethod
    def extract_variant(cls, target: Tag | BeautifulSoup) -> Optional[Dict[str, str]]:
        variant = {}
        for sel in selectors.VARIANT_SELECTORS:
            elem = target.select_one(sel)
            if elem:
                val = elem.get_text().strip()
                if val:
                    key = "color" if "color" in sel else ("size" if "size" in sel else "style")
                    variant[key] = val
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

        # 1. Look for dropdown options
        options = soup.select("select#native_dropdown_selected_size_name option, select[name*='size_name'] option")
        for opt in options:
            val = opt.get("value")
            txt = opt.get_text(strip=True)
            if not txt or val in ("-1", "", None) or "select" in txt.lower():
                continue
            p_match = re.search(r'₹\s*([\d,]+(?:\.\d+)?)', txt)
            size_clean = re.sub(r'\(₹.*?\)', '', txt).strip()
            if not size_clean or size_clean.lower() in seen_sizes:
                continue
            seen_sizes.add(size_clean.lower())
            v_p = float(p_match.group(1).replace(",", "")) if p_match else (default_price or 0.0)
            variants.append({
                "size": size_clean,
                "price": v_p,
                "mrp": default_mrp,
                "in_stock": True,
                "sku": val,
            })

        # 2. Look for variationValues JSON in scripts
        if not variants:
            for s in soup.find_all("script"):
                txt = s.string or ""
                if "variationValues" in txt and "size_name" in txt:
                    try:
                        m = re.search(r'"variationValues"\s*:\s*(\{.*?\})', txt)
                        if m:
                            vv = json.loads(m.group(1))
                            size_list = vv.get("size_name") or []
                            for sz in size_list:
                                sz_clean = str(sz).strip()
                                if sz_clean and sz_clean.lower() not in seen_sizes:
                                    seen_sizes.add(sz_clean.lower())
                                    variants.append({
                                        "size": sz_clean,
                                        "price": default_price or 0.0,
                                        "mrp": default_mrp,
                                        "in_stock": True,
                                        "sku": None,
                                    })
                    except Exception:
                        pass
                if variants:
                    break

        # 3. Look for Twister size buttons / swatches
        if not variants:
            swatches = soup.select(
                "div#inline-twister-expander-content-size_name li, #variation_size_name li, "
                "ul.a-button-toggle li, li[id^='size_name_'], div#inline-twister-row-size_name li, li[data-asin]"
            )
            for sw in swatches:
                txt_el = sw.select_one("span.a-size-base, span.swatch-title-text-display, input, span.a-button-text")
                txt = (txt_el.get("value") or txt_el.get_text(strip=True)) if txt_el else sw.get_text(strip=True)
                cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', txt).strip()
                if not cleaned or len(cleaned) > 20:
                    continue
                if cleaned.lower() in seen_sizes:
                    continue
                seen_sizes.add(cleaned.lower())

                asin = sw.get("data-defaultasin") or sw.get("data-asin")
                classes = " ".join(sw.get("class", []))
                in_stock = "swatch-unavailable" not in classes and "unavailable" not in classes

                p_el = sw.select_one("span.a-color-price, span.twisterSwatchPrice")
                v_p = SharedNormalizer.clean_price(p_el.get_text()) if p_el else (default_price or 0.0)

                variants.append({
                    "size": cleaned,
                    "price": float(v_p),
                    "mrp": default_mrp,
                    "in_stock": in_stock,
                    "sku": asin,
                })

        return variants

    @classmethod
    def extract_availability(cls, target: Tag | BeautifulSoup, soup: BeautifulSoup) -> Tuple[Any, bool]:
        """
        Scoped stock check on Amazon buybox.
        """
        # Check active buybox cart button
        for sel in selectors.BUYBOX_CART_BUTTONS:
            btn = target.select_one(sel) or soup.select_one(sel)
            if btn:
                return "in_stock", True

        # Check buybox out of stock indicator
        for sel in selectors.BUYBOX_OUT_OF_STOCK_SELECTORS:
            elem = target.select_one(sel) or soup.select_one(sel)
            if elem:
                txt = elem.get_text().strip().lower()
                if "currently unavailable" in txt or "out of stock" in txt:
                    return "out_of_stock", False

        return "in_stock", True
