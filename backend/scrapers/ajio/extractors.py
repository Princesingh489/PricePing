"""
AJIO Extractors
"""
import re
import json
import logging
from typing import Optional, Dict, Any, List, Tuple
from bs4 import BeautifulSoup, Tag

from scrapers.shared.models import PriceCandidate
from scrapers.shared.normalizers import SharedNormalizer
from scrapers.ajio import selectors

logger = logging.getLogger(__name__)


class AjioExtractor:
    @classmethod
    def extract_candidates(cls, soup: BeautifulSoup, target: Tag | BeautifulSoup) -> Tuple[List[PriceCandidate], Dict[str, Any]]:
        candidates: List[PriceCandidate] = []
        meta_data: Dict[str, Any] = {}

        # 1. JSON-LD Extraction (Supporting Product and ProductGroup with hasVariant)
        for script in soup.select('script[type="application/ld+json"]'):
            try:
                content = script.string or script.get_text() or "{}"
                data = json.loads(content)
                items = data if isinstance(data, list) else data.get("@graph", [data])
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    itype = item.get("@type", "")
                    types = itype if isinstance(itype, list) else [itype]
                    if any(t in ("Product", "ProductGroup") for t in types):
                        if item.get("name") and not meta_data.get("json_ld_name"):
                            meta_data["json_ld_name"] = item.get("name")
                        if item.get("image") and not meta_data.get("json_ld_image"):
                            meta_data["json_ld_image"] = item.get("image")
                        b_val = item.get("brand")
                        if b_val:
                            b_name = b_val.get("name") if isinstance(b_val, dict) else str(b_val)
                            if b_name and not meta_data.get("json_ld_brand"):
                                meta_data["json_ld_brand"] = b_name

                        # Base Offers
                        offers = item.get("offers", {})
                        offer_list = offers if isinstance(offers, list) else [offers]
                        for off in offer_list:
                            if isinstance(off, dict):
                                if off.get("price"):
                                    p = SharedNormalizer.clean_price(off["price"])
                                    if p:
                                        candidates.append(PriceCandidate(value=p, source="ajio_json_ld_offer", category="selling_price", confidence=96))
                                if off.get("highPrice"):
                                    mrp = SharedNormalizer.clean_price(off["highPrice"])
                                    if mrp:
                                        candidates.append(PriceCandidate(value=mrp, source="ajio_json_ld_mrp", category="mrp", confidence=92))
                                if off.get("lowPrice") and not off.get("price"):
                                    lp = SharedNormalizer.clean_price(off["lowPrice"])
                                    if lp:
                                        candidates.append(PriceCandidate(value=lp, source="ajio_json_ld_low_price", category="selling_price", confidence=94))
                                if off.get("availability"):
                                    meta_data["json_ld_availability"] = "in_stock" if "InStock" in str(off["availability"]) else "out_of_stock"

                        # Per-Variant Offers (Apparel/Footwear sizes)
                        for var in item.get("hasVariant", []):
                            if isinstance(var, dict):
                                v_off = var.get("offers", {})
                                v_offers = v_off if isinstance(v_off, list) else [v_off]
                                for vo in v_offers:
                                    if isinstance(vo, dict):
                                        if vo.get("price"):
                                            p = SharedNormalizer.clean_price(vo["price"])
                                            if p:
                                                candidates.append(PriceCandidate(value=p, source="ajio_json_ld_variant_price", category="selling_price", confidence=95))
                                        if vo.get("highPrice"):
                                            mrp = SharedNormalizer.clean_price(vo["highPrice"])
                                            if mrp:
                                                candidates.append(PriceCandidate(value=mrp, source="ajio_json_ld_variant_mrp", category="mrp", confidence=91))
                                        if vo.get("lowPrice"):
                                            lp = SharedNormalizer.clean_price(vo["lowPrice"])
                                            if lp:
                                                candidates.append(PriceCandidate(value=lp, source="ajio_json_ld_variant_low_price", category="selling_price", confidence=93))

                        agg = item.get("aggregateRating", {})
                        if agg and isinstance(agg, dict):
                            meta_data["rating"] = SharedNormalizer.parse_rating(agg.get("ratingValue"))
                            meta_data["rating_count"] = SharedNormalizer.parse_count(agg.get("ratingCount"))
            except Exception:
                pass

        # 2. window.__PRELOADED_STATE__ Extraction
        for script in soup.find_all("script"):
            txt = script.string or script.get_text() or ""
            if "window.__PRELOADED_STATE__" in txt:
                try:
                    idx = txt.find("window.__PRELOADED_STATE__")
                    eq_idx = txt.find("=", idx)
                    if eq_idx != -1:
                        json_str = txt[eq_idx + 1:].strip()
                        if json_str.endswith(";"):
                            json_str = json_str[:-1].strip()
                        ps = None
                        try:
                            ps = json.loads(json_str)
                        except Exception:
                            m = re.search(r'window\.__PRELOADED_STATE__\s*=\s*(\{.*?\});', txt, re.DOTALL)
                            if m:
                                ps = json.loads(m.group(1))
                        if ps and isinstance(ps, dict):
                            p = ps.get("product")
                            pd = p.get("productDetails") if isinstance(p, dict) else None
                            if not isinstance(pd, dict):
                                pd = ps.get("productDetails")
                            if isinstance(pd, dict):
                                if pd.get("name") and not meta_data.get("preloaded_name"):
                                    meta_data["preloaded_name"] = pd.get("name")
                                if pd.get("brandName") and not meta_data.get("preloaded_brand"):
                                    meta_data["preloaded_brand"] = pd.get("brandName")

                                p_obj = pd.get("price", {})
                                p_val = p_obj.get("value") if isinstance(p_obj, dict) else p_obj
                                if p_val:
                                    clean_p = SharedNormalizer.clean_price(p_val)
                                    if clean_p:
                                        candidates.append(PriceCandidate(value=clean_p, source="ajio_preloaded_price", category="selling_price", confidence=98))

                                w_obj = pd.get("wasPriceData", {})
                                w_val = w_obj.get("value") if isinstance(w_obj, dict) else w_obj
                                if w_val:
                                    clean_w = SharedNormalizer.clean_price(w_val)
                                    if clean_w:
                                        candidates.append(PriceCandidate(value=clean_w, source="ajio_preloaded_mrp", category="mrp", confidence=95))

                                if isinstance(p_obj, dict) and p_obj.get("discountValue"):
                                    meta_data["preloaded_discount"] = float(p_obj["discountValue"])

                                imgs = pd.get("images", [])
                                if imgs and isinstance(imgs, list):
                                    for im in imgs:
                                        if isinstance(im, dict) and im.get("url"):
                                            meta_data["preloaded_image"] = im["url"]
                                            break
                except Exception:
                    pass

        # 3. OpenGraph / Meta Tag Extraction (universal fallback across all product categories)
        for meta_p in soup.select("meta[property='product:price:amount'], meta[property='og:price:amount'], meta[name='twitter:data1']"):
            content = meta_p.get("content")
            if content:
                val = SharedNormalizer.clean_price(content)
                if val and val > 0:
                    candidates.append(PriceCandidate(value=val, source="ajio_meta_price", category="selling_price", confidence=90))

        for meta_m in soup.select("meta[property='product:original_price:amount'], meta[property='product:mrp']"):
            content = meta_m.get("content")
            if content:
                val = SharedNormalizer.clean_price(content)
                if val and val > 0:
                    candidates.append(PriceCandidate(value=val, source="ajio_meta_mrp", category="mrp", confidence=88))

        og_t = soup.select_one("meta[property='og:title'], meta[name='twitter:title']")
        if og_t and og_t.get("content") and not meta_data.get("og_title"):
            meta_data["og_title"] = og_t["content"].strip()

        og_b = soup.select_one("meta[property='product:brand'], meta[name='brand']")
        if og_b and og_b.get("content") and not meta_data.get("og_brand"):
            meta_data["og_brand"] = og_b["content"].strip()

        # 4. Visible price
        for sel in selectors.PRICE_SELECTORS:
            for elem in target.select(sel):
                val = SharedNormalizer.clean_price(elem.get_text())
                if val and val > 0:
                    candidates.append(PriceCandidate(value=val, source=f"ajio_{sel}", category="selling_price", confidence=95, raw_text=elem.get_text()))

        # 5. MRP
        for sel in selectors.MRP_SELECTORS:
            for elem in target.select(sel):
                val = SharedNormalizer.clean_price(elem.get_text())
                if val and val > 0:
                    candidates.append(PriceCandidate(value=val, source=f"ajio_mrp_{sel}", category="mrp", confidence=90, raw_text=elem.get_text()))

        return candidates, meta_data

    @staticmethod
    def _is_valid_image(url: Optional[str]) -> bool:
        if not url or not isinstance(url, str):
            return False
        u = url.lower().strip()
        if not u.startswith("http"):
            return False
        if any(bad in u for bad in ["logo", "icon", ".svg", "trust_marker", "banner", "spinner", "badge", "avatar"]):
            return False
        return True

    @classmethod
    def extract_image(cls, target: Tag | BeautifulSoup, soup: BeautifulSoup) -> Optional[str]:
        # 1. Check OpenGraph image first (always canonical high-res)
        og_img = soup.select_one("meta[property='og:image'], meta[property='og:image:secure_url'], meta[name='twitter:image']")
        if og_img and og_img.get("content") and cls._is_valid_image(og_img["content"]):
            return og_img["content"].strip()

        # 2. Check JSON-LD image
        for script in soup.select('script[type="application/ld+json"]'):
            try:
                data = json.loads(script.string or script.get_text() or "{}")
                items = data if isinstance(data, list) else data.get("@graph", [data])
                for item in items:
                    if isinstance(item, dict) and item.get("image"):
                        img = item["image"]
                        img_url = img if isinstance(img, str) else (img.get("url") if isinstance(img, dict) else None)
                        if img_url and cls._is_valid_image(img_url):
                            return img_url.strip()
            except Exception:
                pass

        # 3. DOM selectors
        for sel in selectors.IMAGE_SELECTORS:
            for elem in target.select(sel):
                src = elem.get("src") or elem.get("data-src")
                if src and cls._is_valid_image(src):
                    return src.strip()
        return None

    @classmethod
    def extract_images(cls, soup: BeautifulSoup, target: Tag | BeautifulSoup) -> List[str]:
        images: List[str] = []
        seen = set()

        def add_img(u: Optional[str]):
            if not u or not cls._is_valid_image(u):
                return
            clean_u = u.strip()
            if clean_u not in seen:
                seen.add(clean_u)
                images.append(clean_u)

        # OpenGraph
        og_img = soup.select_one("meta[property='og:image'], meta[property='og:image:secure_url']")
        if og_img and og_img.get("content"):
            add_img(og_img["content"])

        # JSON-LD
        for script in soup.select('script[type="application/ld+json"]'):
            try:
                data = json.loads(script.string or script.get_text() or "{}")
                items = data if isinstance(data, list) else data.get("@graph", [data])
                for item in items:
                    if isinstance(item, dict):
                        img_field = item.get("image")
                        if isinstance(img_field, list):
                            for i in img_field:
                                add_img(i if isinstance(i, str) else i.get("url"))
                        elif isinstance(img_field, str):
                            add_img(img_field)
            except Exception:
                pass

        # DOM images
        for sel in selectors.IMAGE_SELECTORS:
            for elem in target.select(sel):
                add_img(elem.get("src") or elem.get("data-src"))

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

        # 1. URL pattern for color: e.g. 460788224_black, 443666961_olive
        m = re.search(r'_([a-zA-Z]+)(?:[/?#]|$)', url)
        if m:
            variant["color"] = m.group(1).title()

        # 2. Query params for size or color
        from urllib.parse import urlparse, parse_qs
        try:
            parsed = urlparse(url)
            qs = parse_qs(parsed.query)
            for k in ["size", "sz", "selectedSize", "size_name"]:
                if k in qs and qs[k]:
                    variant["size"] = qs[k][0].strip()
                    break
            for k in ["color", "shade", "colour"]:
                if k in qs and qs[k] and "color" not in variant:
                    variant["color"] = qs[k][0].title().strip()
                    break
        except Exception:
            pass

        # 3. Check window.__PRELOADED_STATE__ for preselected size or color
        if "size" not in variant or "color" not in variant:
            for script in soup.find_all("script"):
                txt = script.string or script.get_text() or ""
                if "window.__PRELOADED_STATE__" in txt:
                    try:
                        idx = txt.find("window.__PRELOADED_STATE__")
                        eq_idx = txt.find("=", idx)
                        if eq_idx != -1:
                            json_str = txt[eq_idx + 1:].strip().rstrip(";")
                            data = json.loads(json_str)
                            if isinstance(data, dict):
                                prod = data.get("product")
                                if isinstance(prod, dict):
                                    sel_sz = prod.get("selectedSizeName")
                                    if sel_sz and "size" not in variant:
                                        variant["size"] = str(sel_sz).strip()
                                    pd = prod.get("productDetails")
                                    if isinstance(pd, dict):
                                        fnl = pd.get("fnlColorVariantData")
                                        if isinstance(fnl, dict):
                                            c_val = fnl.get("color") or fnl.get("colordescription")
                                            if c_val and "color" not in variant:
                                                variant["color"] = str(c_val).title().strip()
                    except Exception:
                        pass
                    break

        # 4. Visible active size swatches in DOM
        if "size" not in variant:
            for sel in selectors.ACTIVE_SIZE_SELECTORS:
                elem = target.select_one(sel) or soup.select_one(sel)
                if elem:
                    txt = elem.get_text().strip()
                    if txt and len(txt) <= 15:
                        variant["size"] = txt
                        break

        # 5. Visible active color swatches in DOM
        if "color" not in variant:
            for sel in selectors.ACTIVE_COLOR_SELECTORS:
                elem = target.select_one(sel) or soup.select_one(sel)
                if elem:
                    txt = elem.get_text().strip() or elem.get("title") or elem.get("data-color")
                    if txt and len(txt) <= 25:
                        variant["color"] = txt.title()
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

        # 1. JSON-LD hasVariant extraction (highest fidelity for size, price, stock)
        for script in soup.select('script[type="application/ld+json"]'):
            try:
                content = script.string or script.get_text() or "{}"
                data = json.loads(content)
                items = data if isinstance(data, list) else data.get("@graph", [data])
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    for v in item.get("hasVariant", []):
                        if not isinstance(v, dict):
                            continue
                        label = str(v.get("size") or v.get("name") or "").strip()
                        if not label or label.lower() in seen_sizes:
                            continue
                        seen_sizes.add(label.lower())
                        v_off = v.get("offers", {})
                        if isinstance(v_off, list) and v_off:
                            v_off = v_off[0]
                        v_price = default_price or 0.0
                        v_mrp = default_mrp
                        in_stock = True
                        if isinstance(v_off, dict):
                            if v_off.get("price"):
                                v_price = float(v_off["price"])
                            elif v_off.get("lowPrice"):
                                v_price = float(v_off["lowPrice"])
                            if v_off.get("highPrice"):
                                v_mrp = float(v_off["highPrice"])
                            if v_off.get("availability"):
                                in_stock = "InStock" in str(v_off["availability"])
                        variants.append({
                            "size": label,
                            "price": v_price if v_price > 0 else (default_price or 0.0),
                            "mrp": v_mrp if v_mrp and v_mrp > 0 else default_mrp,
                            "in_stock": in_stock,
                            "sku": str(v.get("sku") or ""),
                        })
            except Exception:
                pass

        # 2. Parse window.__PRELOADED_STATE__
        for script in soup.find_all("script"):
            txt = script.string or ""
            if "__PRELOADED_STATE__" in txt or "productDetails" in txt:
                try:
                    idx = txt.find("window.__PRELOADED_STATE__")
                    eq_idx = txt.find("=", idx)
                    if eq_idx != -1:
                        json_str = txt[eq_idx + 1:].strip()
                        if json_str.endswith(";"):
                            json_str = json_str[:-1].strip()
                        data = None
                        try:
                            data = json.loads(json_str)
                        except Exception:
                            m = re.search(r'window\.__PRELOADED_STATE__\s*=\s*(\{.*?\});', txt, re.DOTALL)
                            if m:
                                data = json.loads(m.group(1))
                        if data and isinstance(data, dict):
                            p = data.get("product")
                            prod_data = p.get("productDetails") if isinstance(p, dict) else None
                            if not isinstance(prod_data, dict):
                                prod_data = data.get("productDetails")
                            if isinstance(prod_data, dict):
                                fnl_data = prod_data.get("fnlColorVariantData")
                                if not isinstance(fnl_data, dict):
                                    fnl_data = {}
                                size_variants = fnl_data.get("variants") or prod_data.get("variants", [])
                            for v in size_variants:
                                label = str(v.get("size") or v.get("variantValue") or v.get("sizeName") or "").strip()
                                if not label or label.lower() in seen_sizes:
                                    continue
                                seen_sizes.add(label.lower())
                                v_price = float(v.get("price", {}).get("value") if isinstance(v.get("price"), dict) else (v.get("price") or default_price or 0.0))
                                v_mrp = float(v.get("wasPriceData", {}).get("value") if isinstance(v.get("wasPriceData"), dict) else (v.get("mrp") or default_mrp or v_price))
                                in_stock = bool(v.get("inStock", True))
                                variants.append({
                                    "size": label,
                                    "price": v_price if v_price > 0 else (default_price or 0.0),
                                    "mrp": v_mrp if v_mrp > 0 else default_mrp,
                                    "in_stock": in_stock,
                                    "sku": str(v.get("code") or ""),
                                })
                except Exception:
                    pass

        # 3. DOM fallback: Size variant swatches
        if not variants:
            size_items = target.select("div.size-variant-item, div.circle.size-variant-item, div[class*='size-swatch']")
            if not size_items:
                size_items = soup.select("div.size-variant-item, div.circle.size-variant-item, div[class*='size-swatch']")

            for item in size_items:
                txt = item.get_text(strip=True)
                cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', txt).strip()
                if not cleaned or len(cleaned) > 15:
                    continue
                if cleaned.lower() in seen_sizes:
                    continue
                seen_sizes.add(cleaned.lower())

                item_classes = " ".join(item.get("class", []))
                in_stock = "size-instock" in item_classes or "available" in item_classes or not ("size-outstock" in item_classes or "disabled" in item_classes)
                item_p = SharedNormalizer.clean_price(item.get_text()) or default_price or 0.0

                variants.append({
                    "size": cleaned,
                    "price": float(item_p),
                    "mrp": default_mrp,
                    "in_stock": in_stock,
                    "sku": item.get("data-code") or None,
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
