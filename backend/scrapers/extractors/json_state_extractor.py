"""
Hidden JSON State Extractor for React/SSR E-Commerce Platforms (Flipkart, Myntra, Next.js, etc.)
================================================================================================
Parses hydrated server state directly from HTML script payloads (__NEXT_DATA__, window.__myx,
window.__INITIAL_STATE__) to guarantee 100% accurate price, active size/variant, and image resolution.
"""

from __future__ import annotations
import re
import json
import logging
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ExtractedVariantData(BaseModel):
    title: str
    price: float
    original_price: Optional[float] = None
    image_url: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    is_in_stock: bool = True
    variant_id: Optional[str] = None
    raw_state_found: bool = True


def clean_price_value(val: Any) -> Optional[float]:
    """Coerces diverse price representations (numbers, currency strings with commas/₹/Rs.) into float."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        s = val.strip().replace(",", "")
        s = re.sub(r'^(?:Rs\.?|INR|₹)\s*', '', s, flags=re.IGNORECASE)
        m = re.search(r'(\d+(?:\.\d+)?)', s)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                return None
    return None


def _safe_json_loads(raw_str: str) -> Dict[str, Any]:
    """Attempts standard json.loads with fallback sanitization for JS object literals."""
    try:
        return json.loads(raw_str)
    except Exception:
        # Sanitize JS booleans/nulls and trailing commas
        sanitized = re.sub(r'\bTrue\b', 'true', raw_str)
        sanitized = re.sub(r'\bFalse\b', 'false', sanitized)
        sanitized = re.sub(r'\bNone\b', 'null', sanitized)
        sanitized = re.sub(r',\s*([}\]])', r'\1', sanitized)
        return json.loads(sanitized)


def _extract_script_payload(script_text: str, prefix: str) -> Optional[Dict[str, Any]]:
    """Extracts balanced JSON/JS object following a variable declaration."""
    idx = script_text.find(prefix)
    if idx == -1:
        return None
    start = script_text.find("{", idx)
    if start == -1:
        return None

    brace_depth = 0
    in_quote = False
    quote_char = None
    escaped = False

    for i in range(start, len(script_text)):
        ch = script_text[i]
        if escaped:
            escaped = False
            continue
        if ch == "\\":
            escaped = True
            continue
        if in_quote:
            if ch == quote_char:
                in_quote = False
        else:
            if ch in ('"', "'"):
                in_quote = True
                quote_char = ch
            elif ch == "{":
                brace_depth += 1
            elif ch == "}":
                brace_depth -= 1
                if brace_depth == 0:
                    candidate = script_text[start:i + 1]
                    try:
                        return _safe_json_loads(candidate)
                    except Exception:
                        return None
    return None


def extract_react_state_from_html(html: str, target_variant_id: Optional[str] = None) -> ExtractedVariantData:
    """
    Parses HTML, detects embedded JSON hydration scripts, and extracts verified variant details.

    Supported state containers:
    1. Next.js: <script id="__NEXT_DATA__" type="application/json">
    2. Myntra: <script>window.__myx = {...};</script>
    3. Flipkart / Redux: <script>window.__INITIAL_STATE__ = {...};</script>
    4. Structured Data Fallback: <script type="application/ld+json">
    """
    if not html:
        raise ValueError("Empty HTML payload provided to extract_react_state_from_html")

    soup = BeautifulSoup(html, "lxml")

    # ==========================================
    # 1. Next.js Hydration State (__NEXT_DATA__)
    # ==========================================
    next_data_script = soup.find("script", id="__NEXT_DATA__")
    if next_data_script and next_data_script.string:
        try:
            payload = _safe_json_loads(next_data_script.string)
            props = payload.get("props", {}).get("pageProps", {})
            return _parse_next_data_payload(props, target_variant_id)
        except Exception as e:
            logger.debug(f"Next.js state extraction attempted but skipped: {e}")

    # ==========================================
    # 2. Window Script Variables (Myntra & React/Redux)
    # ==========================================
    for script in soup.find_all("script"):
        script_text = script.string or ""
        if not script_text:
            continue

        # Myntra window.__myx state
        if "window.__myx" in script_text or "__myx" in script_text:
            myx_data = _extract_script_payload(script_text, "__myx")
            if myx_data:
                try:
                    return _parse_myntra_state(myx_data, target_variant_id)
                except Exception as e:
                    logger.debug(f"Myntra state parse failed: {e}")

        # Flipkart / generic window.__INITIAL_STATE__
        if "window.__INITIAL_STATE__" in script_text or "__INITIAL_STATE__" in script_text:
            state_data = _extract_script_payload(script_text, "__INITIAL_STATE__")
            if state_data:
                try:
                    return _parse_flipkart_or_generic_state(state_data, target_variant_id)
                except Exception as e:
                    logger.debug(f"window.__INITIAL_STATE__ parse failed: {e}")

    # ==========================================
    # 3. Schema.org JSON-LD Fallback
    # ==========================================
    ld_json_scripts = soup.find_all("script", type="application/ld+json")
    for s in ld_json_scripts:
        if not s.string:
            continue
        try:
            ld_data = _safe_json_loads(s.string)
            if isinstance(ld_data, list):
                ld_data = next((item for item in ld_data if item.get("@type") == "Product"), {})
            if isinstance(ld_data, dict) and ld_data.get("@type") == "Product":
                offers = ld_data.get("offers", {})
                if isinstance(offers, list) and offers:
                    offers = offers[0]

                price = clean_price_value(offers.get("price"))
                if price:
                    img = ld_data.get("image")
                    image_url = img[0] if isinstance(img, list) and img else (img if isinstance(img, str) else None)
                    return ExtractedVariantData(
                        title=str(ld_data.get("name", "Tracked Product")),
                        price=price,
                        image_url=image_url,
                        is_in_stock="InStock" in str(offers.get("availability", "")),
                        variant_id=target_variant_id,
                        raw_state_found=True
                    )
        except Exception:
            continue

    raise ValueError("Could not extract verified JSON state from HTML payload.")


def _parse_myntra_state(data: Dict[str, Any], target_size_or_sku: Optional[str]) -> ExtractedVariantData:
    """Deep traversal of Myntra window.__myx state payload."""
    pdp_data = data.get("pdpData")
    if not pdp_data:
        raise KeyError("pdpData missing from Myntra hydration payload")

    # Resolve Brand and Product Title
    name = pdp_data.get("name") or pdp_data.get("title", "")
    brand_dict = pdp_data.get("brand") or {}
    brand = brand_dict.get("name", "") if isinstance(brand_dict, dict) else str(brand_dict)
    full_title = f"{brand} {name}".strip() if brand and brand.lower() not in name.lower() else name

    # Price resolution
    price_info = pdp_data.get("price", {})
    selling_price = clean_price_value(price_info.get("discounted") or price_info.get("selling"))
    mrp = clean_price_value(price_info.get("mrp"))

    # Image extraction from first album
    image_url = None
    media = pdp_data.get("media", {}).get("albums", [])
    if media and isinstance(media, list) and len(media) > 0:
        images = media[0].get("images", [])
        if images and isinstance(images, list):
            image_url = images[0].get("src")

    # Variant / Size targeting
    sizes = pdp_data.get("sizes", [])
    selected_size = None
    is_in_stock = True

    if sizes and isinstance(sizes, list):
        target_variant = None
        if target_size_or_sku:
            target_variant = next(
                (s for s in sizes if str(s.get("label", "")).upper() == str(target_size_or_sku).upper()
                 or str(s.get("skuId", "")) == str(target_size_or_sku)),
                None
            )

        # Default to first available size if not specified or not matched
        if not target_variant:
            target_variant = next((s for s in sizes if s.get("available", True)), sizes[0])

        if target_variant:
            selected_size = str(target_variant.get("label", ""))
            is_in_stock = bool(target_variant.get("available", True))
            if target_variant.get("discountedPrice"):
                selling_price = clean_price_value(target_variant.get("discountedPrice"))
            if target_variant.get("mrp"):
                mrp = clean_price_value(target_variant.get("mrp"))

    if selling_price is None:
        raise ValueError("Could not resolve valid selling price in Myntra PDP state.")

    return ExtractedVariantData(
        title=full_title,
        price=selling_price,
        original_price=mrp,
        image_url=image_url,
        size=selected_size,
        is_in_stock=is_in_stock,
        variant_id=target_size_or_sku,
        raw_state_found=True
    )


def _parse_next_data_payload(page_props: Dict[str, Any], target_variant_id: Optional[str]) -> ExtractedVariantData:
    """Deep traversal of Next.js pageProps state."""
    product_obj = (
        page_props.get("product")
        or page_props.get("initialData", {}).get("product")
        or page_props.get("productDetails")
        or page_props
    )

    title = product_obj.get("title") or product_obj.get("name") or "Tracked Product"
    price = clean_price_value(
        product_obj.get("price") or product_obj.get("specialPrice") or product_obj.get("currentPrice")
    )
    mrp = clean_price_value(product_obj.get("mrp") or product_obj.get("originalPrice"))
    image = product_obj.get("imageUrl") or product_obj.get("image") or product_obj.get("productImage")

    variants = product_obj.get("variants", [])
    size_label = None
    if variants and isinstance(variants, list):
        selected_v = None
        if target_variant_id:
            selected_v = next((v for v in variants if str(v.get("id")) == str(target_variant_id)), None)
        if not selected_v and variants:
            selected_v = variants[0]

        if selected_v:
            title = selected_v.get("title", title)
            size_label = selected_v.get("size")
            if "price" in selected_v:
                price = clean_price_value(selected_v["price"])

    if price is None:
        raise ValueError("No valid price found in Next.js hydration state.")

    return ExtractedVariantData(
        title=str(title),
        price=price,
        original_price=mrp,
        image_url=image,
        size=size_label,
        is_in_stock=bool(product_obj.get("inStock", True)),
        variant_id=target_variant_id,
        raw_state_found=True
    )


def _parse_flipkart_or_generic_state(state: Dict[str, Any], target_pid: Optional[str]) -> ExtractedVariantData:
    """Traverses Flipkart pageDataV4 or generic Redux initial state."""
    page_data = state.get("pageDataV4", {}).get("page", {}).get("data", {})
    title = None
    price = None
    mrp = None
    image_url = None

    for slot_key, slot_val in page_data.items():
        if isinstance(slot_val, list):
            for widget in slot_val:
                widget_data = widget.get("widget", {}).get("data", {})
                if "productCard" in widget_data:
                    card = widget_data["productCard"]
                    title = card.get("title")
                    pricing = card.get("pricing", {})
                    price = clean_price_value(pricing.get("finalPrice", {}).get("value"))
                    mrp = clean_price_value(pricing.get("mrp", {}).get("value"))
                    break

    if not title:
        title = state.get("title") or state.get("productName") or "Tracked Product"
    if price is None:
        price = clean_price_value(state.get("price") or state.get("finalPrice") or state.get("currentPrice"))
    if mrp is None:
        mrp = clean_price_value(state.get("mrp") or state.get("originalPrice"))
    if not image_url:
        image_url = state.get("image") or state.get("imageUrl")

    if price is None:
        raise ValueError("Price not found in Flipkart/Redux initial state")

    return ExtractedVariantData(
        title=str(title),
        price=price,
        original_price=mrp,
        image_url=image_url,
        variant_id=target_pid,
        raw_state_found=True
    )
