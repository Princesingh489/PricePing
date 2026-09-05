"""
Flipkart Extractors
"""
import re
import json
import logging
from urllib.parse import parse_qs, urlparse
from typing import Optional, Dict, Any, List, Tuple
from bs4 import BeautifulSoup, Tag

from db.models import AvailabilityEnum
from scrapers.shared.models import PriceCandidate
from scrapers.shared.normalizers import SharedNormalizer
from scrapers.flipkart import selectors

logger = logging.getLogger(__name__)


class FlipkartExtractor:
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
                            candidates.append(PriceCandidate(value=val, source="flipkart_json_ld_offer", category="selling_price", confidence=95))
                    agg = data.get("aggregateRating", {})
                    if agg:
                        meta_data["rating"] = SharedNormalizer.parse_rating(agg.get("ratingValue"))
                        meta_data["rating_count"] = SharedNormalizer.parse_count(agg.get("ratingCount"))
                        meta_data["review_count"] = SharedNormalizer.parse_count(agg.get("reviewCount"))
            except Exception:
                pass

        # 2. Visible selling price
        for sel in selectors.PRICE_SELECTORS:
            for elem in target.select(sel):
                val = SharedNormalizer.clean_price(elem.get_text())
                if val and val > 0:
                    conf = 100 if "CxhGGd" in sel else 95
                    candidates.append(PriceCandidate(value=val, source=f"flipkart_{sel}", category="selling_price", confidence=conf, raw_text=elem.get_text()))

        # 3. MRP strikethrough (Search both scoped target and entire soup)
        seen_mrps = set()
        for sel in selectors.MRP_SELECTORS:
            for elem in (target.select(sel) + soup.select(sel)):
                val = SharedNormalizer.clean_price(elem.get_text())
                if val and val > 0 and val not in seen_mrps:
                    seen_mrps.add(val)
                    candidates.append(PriceCandidate(value=val, source=f"flipkart_mrp_{sel}", category="mrp", confidence=90, raw_text=elem.get_text()))

        # 4. Embedded script MRP / Discount
        for script in soup.select('script'):
            txt = script.string or ""
            if "pricing" in txt or "pageData" in txt or "window.__INITIAL_STATE__" in txt:
                try:
                    m_mrp = re.search(r'["\']mrp["\']\s*:\s*\{\s*["\']decimalValue["\']\s*:\s*["\']([\d.]+)["\']', txt)
                    if m_mrp:
                        val = float(m_mrp.group(1))
                        if val > 0 and val not in seen_mrps:
                            seen_mrps.add(val)
                            candidates.append(PriceCandidate(value=val, source="flipkart_embedded_mrp", category="mrp", confidence=95))

                    m_strike = re.search(r'["\']strikeOffPrice["\']\s*:\s*([\d.]+)', txt)
                    if m_strike:
                        val = float(m_strike.group(1))
                        if val > 0 and val not in seen_mrps:
                            seen_mrps.add(val)
                            candidates.append(PriceCandidate(value=val, source="flipkart_embedded_strike_price", category="mrp", confidence=95))

                    m_disc = re.search(r'["\']totalDiscount["\']\s*:\s*(\d+)', txt)
                    if m_disc and "extracted_discount" not in meta_data:
                        meta_data["extracted_discount"] = float(m_disc.group(1))
                except Exception:
                    pass

        # 5. Discount badge
        for sel in selectors.DISCOUNT_SELECTORS:
            for elem in (target.select(sel) + soup.select(sel)):
                d_match = re.search(r'(\d+)', elem.get_text())
                if d_match and "extracted_discount" not in meta_data:
                    meta_data["extracted_discount"] = float(d_match.group(1))
                    break

        # 6. Modern RNW Price container (--sm-order:7 or elements containing Hot Deal / special price)
        price_box = soup.find(lambda t: t.has_attr('style') and "--sm-order:7" in t.get('style', ''))
        if not price_box:
            for el in soup.find_all(lambda t: t.string and ('Hot Deal' in t.string or '₹' in t.string)):
                p = el.find_parent(lambda t: '₹' in t.get_text() and any(c.isdigit() for c in t.get_text()))
                if p and len(p.get_text()) < 200:
                    price_box = p
                    break
        if price_box:
            txt = price_box.get_text(separator=' ', strip=True)
            found_selling = [float(p.replace(',', '')) for p in re.findall(r'(?:₹|Rs\.?)\s*([\d,]+)', txt)]
            for s_val in found_selling:
                if s_val > 0:
                    candidates.append(PriceCandidate(value=s_val, source="flipkart_rnw_price_box", category="selling_price", confidence=100, raw_text=txt))

            found_mrps = [float(p.replace(',', '')) for p in re.findall(r'(?:^|\s)([\d,]+)(?:\s*(?:₹|Rs\.?))', txt)]
            for m_val in found_mrps:
                if m_val > 0 and m_val not in seen_mrps:
                    seen_mrps.add(m_val)
                    candidates.append(PriceCandidate(value=m_val, source="flipkart_rnw_mrp_box", category="mrp", confidence=95, raw_text=txt))

            found_discs = [float(d) for d in re.findall(r'(\d+)%', txt)]
            if found_discs and "extracted_discount" not in meta_data:
                meta_data["extracted_discount"] = found_discs[0]

        return candidates, meta_data

    @classmethod
    def extract_variant(cls, soup: BeautifulSoup, target: Tag | BeautifulSoup, url: str) -> Dict[str, str]:
        """
        Extract selected variant attributes (size, color, storage, lid, pid)
        from both URL parameters and active DOM buttons/swatches.
        """
        variant: Dict[str, str] = {}

        # 1. URL query parameters
        try:
            parsed = urlparse(url)
            qs = parse_qs(parsed.query)
            if "size" in qs and qs["size"]:
                variant["size"] = qs["size"][0]
            if "color" in qs and qs["color"]:
                variant["color"] = qs["color"][0]
            if "lid" in qs and qs["lid"]:
                variant["lid"] = qs["lid"][0]
            if "pid" in qs and qs["pid"]:
                variant["pid"] = qs["pid"][0]
        except Exception:
            pass

        # 2. Active DOM Size button
        for sel in selectors.ACTIVE_SIZE_SELECTORS:
            elem = target.select_one(sel) or soup.select_one(sel)
            if elem:
                txt = elem.get_text().strip()
                if txt and len(txt) <= 15:
                    variant["size"] = txt
                    break

        # 3. Active DOM Color swatch
        # 3. Active DOM Color swatch
        for sel in selectors.ACTIVE_COLOR_SELECTORS:
            elem = target.select_one(sel) or soup.select_one(sel)
            if elem:
                color_name = elem.get("alt") or elem.get("title") or elem.get_text().strip()
                if color_name:
                    variant["color"] = color_name
                    break

        # 4. Title regex for variant specifications e.g. "(Tan , 8)", "(Black, 9)", "(128 GB, Black)"
        page_title = (soup.title.string or "") if soup.title else ""
        if not variant.get("color") or not variant.get("size"):
            m_title_var = re.search(r'\(([^,)]+)\s*,\s*([^)]+)\)', page_title)
            if m_title_var:
                c_cand = m_title_var.group(1).strip()
                s_cand = m_title_var.group(2).strip()
                if not variant.get("color") and c_cand and len(c_cand) <= 20:
                    variant["color"] = c_cand
                if not variant.get("size") and s_cand and len(s_cand) <= 15:
                    variant["size"] = s_cand

        return variant

    @classmethod
    def extract_colors(
        cls,
        soup: BeautifulSoup,
        target: Tag | BeautifulSoup,
        default_price: Optional[float] = None,
        default_mrp: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        colors: List[Dict[str, Any]] = []
        seen_colors = set()

        # 1. From window.__INITIAL_STATE__
        for script in soup.find_all("script"):
            txt = script.string or ""
            if "window.__INITIAL_STATE__" in txt:
                try:
                    m = re.search(r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});', txt, re.DOTALL)
                    if m:
                        data = json.loads(m.group(1))
                        def find_color_swatches(d):
                            if isinstance(d, dict):
                                if d.get("id") == "color" or d.get("attributeType") == "COLOR" or "color" in str(d.get("title", "")).lower():
                                    return d
                                for k, v in d.items():
                                    res = find_color_swatches(v)
                                    if res:
                                        return res
                            elif isinstance(d, list):
                                for item in d:
                                    res = find_color_swatches(item)
                                    if res:
                                        return res
                            return None

                        col_block = find_color_swatches(data)
                        if col_block:
                            swatches = col_block.get("attributeValues") or col_block.get("swatches", [])
                            for s in swatches:
                                c_name = str(s.get("value") or s.get("text") or "").strip()
                                if not c_name or c_name.lower() in seen_colors:
                                    continue
                                seen_colors.add(c_name.lower())
                                img_thumb = s.get("image") or s.get("thumbnail") or s.get("url")
                                if img_thumb and "{@width}" in img_thumb:
                                    img_thumb = img_thumb.replace("{@width}", "128").replace("{@height}", "128")
                                colors.append({
                                    "name": c_name,
                                    "thumbnail": img_thumb,
                                    "price": float(s.get("price") or default_price or 0.0),
                                    "mrp": float(s.get("mrp") or default_mrp or (default_price or 0.0)),
                                    "in_stock": not bool(s.get("disabled", False) or s.get("outOfStock", False)),
                                    "product_url": s.get("actionUrl") or None,
                                })
                except Exception:
                    pass

        # 2. From DOM: Color swatches
        if not colors:
            color_box = soup.find(lambda t: t.has_attr('style') and "--sm-order:3" in t.get('style', ''))
            if not color_box:
                for el in soup.find_all(string=re.compile(r'Selected Color', re.I)):
                    p = el.find_parent(lambda t: len(t.select('img')) >= 1)
                    if p:
                        color_box = p
                        break
            if color_box:
                box_txt = color_box.get_text(strip=True)
                m_col = re.search(r'Selected Color:\s*([a-zA-Z0-9\s-]+)', box_txt)
                sel_color_name = m_col.group(1).strip() if m_col else None

                for a in color_box.select('a'):
                    img = a.select_one('img')
                    thumb = img.get('src') or img.get('data-src') if img else None
                    href = a.get('href', '')
                    if thumb and "{@width}" in thumb:
                        thumb = thumb.replace("{@width}", "128").replace("{@height}", "128")

                    c_name = img.get('alt') or img.get('title') if img else None
                    if not c_name or c_name.lower() in ["image", "thumb", "thumbnail", ""]:
                        t_lower = (thumb or '').lower()
                        if 'black' in t_lower:
                            c_name = 'Black'
                        elif 'blue' in t_lower or 'navy' in t_lower:
                            c_name = 'Blue'
                        elif 'tan' in t_lower or 'brown' in t_lower:
                            c_name = 'Tan'
                        elif sel_color_name and sel_color_name.lower() not in seen_colors:
                            c_name = sel_color_name
                        else:
                            fallback_colors = ["Blue", "Tan", "Black", "Brown", "Grey", "Navy", "Olive"]
                            available = [k for k in fallback_colors if k.lower() not in seen_colors]
                            c_name = available[0] if available else f"Color {len(colors)+1}"

                    if c_name and c_name.lower() not in seen_colors:
                        seen_colors.add(c_name.lower())
                        full_url = f"https://www.flipkart.com{href}" if href.startswith('/') else (href or None)
                        colors.append({
                            "name": c_name,
                            "thumbnail": thumb,
                            "price": default_price,
                            "mrp": default_mrp,
                            "in_stock": True,
                            "product_url": full_url,
                        })

                # Ensure selected color is present in colors list
                if sel_color_name and sel_color_name.lower() not in seen_colors:
                    seen_colors.add(sel_color_name.lower())
                    img_url = cls.extract_image(target, soup)
                    colors.append({
                        "name": sel_color_name,
                        "thumbnail": img_url,
                        "price": default_price,
                        "mrp": default_mrp,
                        "in_stock": True,
                        "product_url": None,
                    })

        # 3. DOM fallback: Color swatches
        if not colors:
            color_elements = target.select("div.swatch, a._2dq9f_, div._2C41yO, div._31p7G_, div._3Oikkn img, a[class*='swatch'] img, li._3V2wfe._3Oikkn img")
            if not color_elements:
                color_elements = soup.select("div.swatch, a._2dq9f_, div._2C41yO, div._31p7G_, div._3Oikkn img, a[class*='swatch'] img, li._3V2wfe._3Oikkn img")

            for el in color_elements:
                img_tag = el if el.name == "img" else el.select_one("img")
                c_name = None
                thumb_src = None
                if img_tag:
                    c_name = img_tag.get("alt") or img_tag.get("title")
                    thumb_src = img_tag.get("src") or img_tag.get("data-src")
                else:
                    c_name = el.get("title") or el.get_text(strip=True)

                if c_name:
                    cleaned_name = re.sub(r'[^a-zA-Z0-9\s-]', '', c_name).strip()
                    if cleaned_name and len(cleaned_name) <= 25 and cleaned_name.lower() not in seen_colors:
                        seen_colors.add(cleaned_name.lower())
                        parent_a = el if el.name == "a" else el.find_parent("a")
                        p_url = parent_a.get("href") if parent_a else None
                        if p_url and p_url.startswith("/"):
                            p_url = f"https://www.flipkart.com{p_url}"
                        colors.append({
                            "name": cleaned_name,
                            "thumbnail": thumb_src,
                            "price": default_price,
                            "mrp": default_mrp,
                            "in_stock": True,
                            "product_url": p_url,
                        })

        return colors

    @classmethod
    def extract_gallery_images(cls, soup: BeautifulSoup, target: Tag | BeautifulSoup) -> List[str]:
        images: List[str] = []
        seen = set()

        # 1. Look for thumbnail list in DOM
        for sel in ["ul._2USHg0 li img", "div.q6DClP img", "div._2E1qri img", "div._2r_T1I img", "img.DByuf4", "img._0DkuPH"]:
            for img in (target.select(sel) + soup.select(sel)):
                src = img.get("src") or img.get("data-src")
                if src and src.startswith("http") and "placeholder" not in src:
                    hd_src = re.sub(r'/(?:128|100|64|50)/(?:128|100|64|50)/', '/832/832/', src)
                    if hd_src not in seen:
                        seen.add(hd_src)
                        images.append(hd_src)

        # 2. Check window.__INITIAL_STATE__ multimedia components
        if len(images) < 2:
            for script in soup.find_all("script"):
                txt = script.string or ""
                if "window.__INITIAL_STATE__" in txt:
                    urls = re.findall(r'https://rukminim\d*\.flixcart\.com/image/[^"\']+', txt)
                    for u in urls:
                        clean_u = u.replace("\\/", "/").replace("{@width}", "832").replace("{@height}", "832")
                        hd_u = re.sub(r'/(?:128|100|64|50)/(?:128|100|64|50)/', '/832/832/', clean_u)
                        if hd_u not in seen and len(images) < 6:
                            seen.add(hd_u)
                            images.append(hd_u)

        return images

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

        # 1. Parse window.__INITIAL_STATE__
        for script in soup.find_all("script"):
            txt = script.string or ""
            if "window.__INITIAL_STATE__" in txt or "pageDataV4" in txt:
                try:
                    m = re.search(r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});', txt, re.DOTALL)
                    if m:
                        data = json.loads(m.group(1))
                        def find_swatches(d):
                            if isinstance(d, dict):
                                if "swatchComponent" in d or "swatches" in d or "attributeValues" in d:
                                    return d
                                for k, v in d.items():
                                    res = find_swatches(v)
                                    if res:
                                        return res
                            elif isinstance(d, list):
                                for item in d:
                                    res = find_swatches(item)
                                    if res:
                                        return res
                            return None

                        swatch_block = find_swatches(data)
                        if swatch_block:
                            items = swatch_block.get("attributeValues") or swatch_block.get("swatches", [])
                            for it in items:
                                label = str(it.get("value") or it.get("text") or "").strip()
                                if not label or label.lower() in seen_sizes:
                                    continue
                                seen_sizes.add(label.lower())
                                v_p = float(it.get("price") or default_price or 0.0)
                                v_m = float(it.get("mrp") or default_mrp or v_p)
                                in_stock = not bool(it.get("disabled", False) or it.get("outOfStock", False))
                                variants.append({
                                    "size": label,
                                    "price": v_p if v_p > 0 else (default_price or 0.0),
                                    "mrp": v_m if v_m > 0 else default_mrp,
                                    "in_stock": in_stock,
                                    "sku": it.get("id") or None,
                                })
                except Exception:
                    pass

        # 2. Modern React Native Web size links: a[href*='swatchAttr=size']
        if not variants:
            rnw_sizes = target.select("a[href*='swatchAttr=size']") + soup.select("a[href*='swatchAttr=size']")
            for a in rnw_sizes:
                s_text = a.get_text(strip=True)
                href = a.get('href', '')
                if s_text and len(s_text) <= 10 and s_text.lower() not in seen_sizes:
                    seen_sizes.add(s_text.lower())
                    style = a.get('style', '') + (a.parent.get('style', '') if a.parent else '')
                    is_out_of_stock = 'opacity:0.' in style or 'line-through' in style or 'strike' in style.lower()
                    full_url = f"https://www.flipkart.com{href}" if href.startswith('/') else (href or None)
                    variants.append({
                        "size": s_text,
                        "price": default_price or 0.0,
                        "mrp": default_mrp,
                        "in_stock": not is_out_of_stock,
                        "product_url": full_url,
                    })

        # 3. DOM fallback: Size swatch pills & buttons
        if not variants:
            swatch_elements = target.select(
                "ul._1q8KgS li a, div._3O_tAk, a.CDDksN, div[class*='size-picker'] a, "
                "a[class*='swatch'], div._21Ahn-, div.K0TWCp a, li._3V2wfe a, div.h-hZtE a"
            )
            if not swatch_elements:
                swatch_elements = soup.select(
                    "ul._1q8KgS li a, div._3O_tAk, a.CDDksN, div[class*='size-picker'] a, "
                    "a[class*='swatch'], div._21Ahn-, div.K0TWCp a, li._3V2wfe a, div.h-hZtE a"
                )

            for el in swatch_elements:
                txt = el.get_text(strip=True)
                cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', txt).strip()
                if not cleaned or len(cleaned) > 15:
                    continue
                if cleaned.lower() in seen_sizes:
                    continue
                seen_sizes.add(cleaned.lower())

                el_classes = " ".join(el.get("class", []))
                parent_classes = " ".join(el.parent.get("class", [])) if el.parent else ""
                in_stock = not ("_3O_tAk" in el_classes or "strike" in el_classes or "disabled" in el_classes or "_3O_tAk" in parent_classes)
                el_p = SharedNormalizer.clean_price(el.get_text()) or default_price or 0.0

                variants.append({
                    "size": cleaned,
                    "price": float(el_p),
                    "mrp": default_mrp,
                    "in_stock": in_stock,
                    "sku": el.get("href") or None,
                })

        return variants

    @classmethod
    def extract_availability(cls, soup: BeautifulSoup, target: Tag | BeautifulSoup) -> Tuple[AvailabilityEnum, bool]:
        """
        Strictly scopes stock check to the main buybox buttons.
        Returns: (AvailabilityEnum, is_buybox_active: bool)
        """
        # Check if active Add To Cart or Buy Now button is present
        for sel in selectors.BUYBOX_CART_BUTTONS:
            btn = target.select_one(sel) or soup.select_one(sel)
            if btn:
                btn_text = btn.get_text().strip().upper()
                if "ADD TO CART" in btn_text or "BUY NOW" in btn_text:
                    return AvailabilityEnum.in_stock, True

        # Check if Notify Me or Out Of Stock is explicitly in the buybox
        for sel in selectors.BUYBOX_OUT_OF_STOCK_SELECTORS:
            elem = target.select_one(sel) or soup.select_one(sel)
            if elem:
                txt = elem.get_text().strip().upper()
                if "NOTIFY ME" in txt or "OUT OF STOCK" in txt or "CURRENTLY UNAVAILABLE" in txt:
                    return AvailabilityEnum.out_of_stock, False

        # Fallback to in_stock if price and title exist
        return AvailabilityEnum.in_stock, True

    @classmethod
    def extract_image(cls, target: Tag | BeautifulSoup, soup: BeautifulSoup) -> Optional[str]:
        for sel in selectors.IMAGE_SELECTORS:
            elem = target.select_one(sel)
            if elem:
                # Check srcset for largest resolution
                srcset = elem.get("srcset")
                if srcset:
                    largest = cls.extract_largest_from_srcset(srcset)
                    if largest:
                        return cls.normalize_flipkart_image(largest)

                src = elem.get("src") or elem.get("data-src")
                if src and "http" in src:
                    return cls.normalize_flipkart_image(src)

        og_img = soup.select_one("meta[property='og:image']")
        if og_img and og_img.get("content"):
            return cls.normalize_flipkart_image(og_img["content"].strip())
        return None

    @classmethod
    def normalize_flipkart_image(cls, url: str) -> str:
        """Upscale thumbnail URLs (128/128) to high-res (832/832)."""
        if not url:
            return url
        url = re.sub(r'/image/\d+/\d+/', '/image/832/832/', url)
        url = re.sub(r'q=\d+', 'q=90', url)
        return url

    @classmethod
    def extract_largest_from_srcset(cls, srcset: str) -> Optional[str]:
        if not srcset:
            return None
        entries = [e.strip().split() for e in srcset.split(',') if e.strip()]
        if not entries:
            return None

        def get_dim(entry):
            if len(entry) > 1:
                m = re.search(r'(\d+)', entry[1])
                if m:
                    return int(m.group(1))
            m_path = re.search(r'/image/(\d+)/(\d+)/', entry[0])
            if m_path:
                return int(m_path.group(1)) * int(m_path.group(2))
            return 0

        sorted_entries = sorted(entries, key=get_dim, reverse=True)
        return sorted_entries[0][0]

    @classmethod
    def extract_brand(cls, target: Tag | BeautifulSoup) -> Optional[str]:
        for sel in selectors.BRAND_SELECTORS:
            elem = target.select_one(sel)
            if elem:
                text = elem.get_text().strip()
                if len(text) >= 2:
                    return text
        return None
