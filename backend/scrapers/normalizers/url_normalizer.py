"""
E-Commerce URL Normalizer for High-Precision Variant Targeting
Sanitizes product URLs, extracts variant identifiers (ASIN, PID, Style ID),
and removes tracking parameters to prevent erroneous fallback variants.
"""

from __future__ import annotations
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class NormalizedURLResult(BaseModel):
    canonical_url: str
    platform: str
    product_id: Optional[str] = None
    variant_id: Optional[str] = None
    original_url: str


class ECommerceURLNormalizer:
    """
    Utility class for e-commerce URL sanitization with variant targeting.
    """

    # Universal ad and analytics tracking parameters to discard
    UNIVERSAL_TRACKING_PARAMS = {
        "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
        "fbclid", "gclid", "gbraid", "wbraid", "ref", "ref_", "tag", "aff_id",
        "aff_sub", "aff_sub2", "sr", "qid", "keywords", "sprefix", "crid",
        "pd_rd_w", "pf_rd_p", "pf_rd_r", "pd_rd_wg", "pd_rd_r", "_encoding",
        "campaign", "dchild", "smid", "th_id", "linkCode", "linkId",
        "marketplace", "otracker", "store", "spotlightTagId", "fm", "iid",
        "ppt", "ppn", "ssid", "rawQuery", "searchQuery"
    }

    @classmethod
    def normalize_amazon(cls, url: str) -> NormalizedURLResult:
        """
        Amazon India normalizer:
        - Extracts ASIN (10 alphanumeric chars, e.g., B0856HNMR7).
        - Preserves variant parameters like th=1 / psc=1 to enforce exact size/color selection.
        - Canonical format: https://www.amazon.in/dp/{ASIN}?th=1&psc=1
        """
        raw = url.strip()
        if not raw.startswith(("http://", "https://")):
            raw = "https://" + raw
        parsed = urlparse(raw)
        netloc = "www.amazon.in" if ("amazon" in parsed.netloc.lower() or "amzn" in parsed.netloc.lower()) else parsed.netloc

        # Extract ASIN from path patterns: /dp/B0..., /gp/product/B0..., /gp/aw/d/B0..., /d/B0...
        asin_match = re.search(r'/(?:dp|gp/product|gp/aw/d|product|d)/([A-Z0-9]{10})', parsed.path, re.IGNORECASE)
        asin = asin_match.group(1).upper() if asin_match else None

        # General ASIN match fallback from path (e.g. /B0BF57RN3K)
        if not asin:
            gen_match = re.search(r'/(B0[A-Z0-9]{8})(?:[/?]|$)', parsed.path, re.IGNORECASE)
            if gen_match:
                asin = gen_match.group(1).upper()

        # Check query parameters as fallback (e.g. ?asin=...)
        query_params = parse_qs(parsed.query)
        if not asin and "asin" in query_params:
            asin = query_params["asin"][0].upper()

        # Shortlink fallback (e.g. amzn.in/d/xyz or amzn.to/xyz)
        if not asin and ("amzn.in" in parsed.netloc.lower() or "amzn.to" in parsed.netloc.lower() or "a.co" in parsed.netloc.lower()):
            short_code = parsed.path.strip("/").split("/")[-1]
            return NormalizedURLResult(
                canonical_url=raw,
                platform="amazon",
                product_id=short_code or "amazon_item",
                variant_id=short_code or "amazon_item",
                original_url=url,
            )

        if not asin:
            clean_path = parsed.path
            return NormalizedURLResult(
                canonical_url=urlunparse(("https", "www.amazon.in", clean_path, "", "", "")),
                platform="amazon",
                product_id=clean_path.strip("/").split("/")[-1] or "amazon_item",
                variant_id=clean_path.strip("/").split("/")[-1] or "amazon_item",
                original_url=url,
            )

        # Preserve variation flags to enforce exact selected variant
        kept_params = {}
        if "th" in query_params:
            kept_params["th"] = query_params["th"][0]
        else:
            kept_params["th"] = "1"

        if "psc" in query_params:
            kept_params["psc"] = query_params["psc"][0]
        else:
            kept_params["psc"] = "1"

        clean_query = urlencode(kept_params)
        canonical_path = f"/dp/{asin}"
        canonical_url = urlunparse(("https", netloc, canonical_path, "", clean_query, ""))

        return NormalizedURLResult(
            canonical_url=canonical_url,
            platform="amazon",
            product_id=asin,
            variant_id=asin,
            original_url=url,
        )

    @classmethod
    def normalize_flipkart(cls, url: str) -> NormalizedURLResult:
        """
        Flipkart normalizer:
        - Flipkart variant targeting depends on the query param `pid`.
        - Strips tracking while preserving `pid` and optional `lid`.
        - Canonical format: https://www.flipkart.com{slug_path}?pid={PID}
        """
        raw = url.strip()
        if not raw.startswith(("http://", "https://")):
            raw = "https://" + raw
        parsed = urlparse(raw)
        query_params = parse_qs(parsed.query)

        # 1. Extract PID (e.g., MOBFWBYZ8GAJ9F7F)
        pid = query_params.get("pid", [None])[0]
        if not pid:
            pid_match = re.search(r'[?&]pid=([A-Za-z0-9_-]+)', raw)
            if pid_match:
                pid = pid_match.group(1)

        clean_path = parsed.path
        clean_path = re.sub(r'/+', '/', clean_path)

        kept_params = {}
        if pid:
            kept_params["pid"] = pid
        else:
            # Check for itm ID in path if PID query is missing
            itm_match = re.search(r'/p/([a-zA-Z0-9_-]+)', clean_path)
            if itm_match:
                pid = itm_match.group(1)
                kept_params["pid"] = pid
            else:
                pid = clean_path.strip("/").split("/")[-1] or "flipkart_item"
                kept_params["pid"] = pid

        if "lid" in query_params:
            kept_params["lid"] = query_params["lid"][0]

        canonical_url = urlunparse(("https", "www.flipkart.com", clean_path, "", urlencode(kept_params), ""))

        return NormalizedURLResult(
            canonical_url=canonical_url,
            platform="flipkart",
            product_id=pid,
            variant_id=pid,
            original_url=url,
        )

    @classmethod
    def normalize_myntra(cls, url: str) -> NormalizedURLResult:
        """
        Myntra normalizer:
        - Extracts numeric Style ID from path: /{category}/{brand}/{slug}/{style_id}/buy
        - Preserves variant parameters: `size` and `skuId`.
        - Canonical format: https://www.myntra.com/{path}/buy?size={size}&skuId={skuId}
        """
        raw = url.strip()
        if not raw.startswith(("http://", "https://")):
            raw = "https://" + raw
        parsed = urlparse(raw)
        path = parsed.path

        # Extract numeric Style ID from path
        style_match = re.search(r'/(\d{5,12})(?:/buy)?/?$', path)
        if not style_match:
            style_match = re.search(r'/(\d{5,12})', path)

        style_id = style_match.group(1) if style_match else (path.strip("/").split("/")[-1] or "myntra_item")

        # Standardize path ending with /buy
        if style_match:
            base_path = re.sub(r'/\d{5,12}(?:/buy)?/?$', f'/{style_id}/buy', path)
        else:
            base_path = path

        if not base_path.startswith('/'):
            base_path = f'/{base_path}'

        query_params = parse_qs(parsed.query)
        kept_params = {}

        if "size" in query_params:
            kept_params["size"] = query_params["size"][0]
        if "skuId" in query_params:
            kept_params["skuId"] = query_params["skuId"][0]

        canonical_url = urlunparse(("https", "www.myntra.com", base_path, "", urlencode(kept_params), ""))

        return NormalizedURLResult(
            canonical_url=canonical_url,
            platform="myntra",
            product_id=style_id,
            variant_id=kept_params.get("skuId") or kept_params.get("size") or style_id,
            original_url=url,
        )

    @classmethod
    def normalize_ajio(cls, url: str) -> NormalizedURLResult:
        """
        AJIO normalizer:
        - Extracts product code (e.g. /p/469034293_blue)
        """
        raw = url.strip()
        if not raw.startswith(("http://", "https://")):
            raw = "https://" + raw
        parsed = urlparse(raw)
        code_match = re.search(r'/p/([a-zA-Z0-9_-]+)', parsed.path)
        code = code_match.group(1) if code_match else (parsed.path.strip("/").split("/")[-1] or "ajio_item")
        clean_path = parsed.path
        canonical_url = urlunparse(("https", "www.ajio.com", clean_path, "", "", ""))
        return NormalizedURLResult(
            canonical_url=canonical_url,
            platform="ajio",
            product_id=code,
            variant_id=code,
            original_url=url
        )

    @classmethod
    def normalize_nykaa(cls, url: str) -> NormalizedURLResult:
        """
        Nykaa normalizer:
        - Extracts SKU / product ID from query parameter `skuId` or path
        """
        raw = url.strip()
        if not raw.startswith(("http://", "https://")):
            raw = "https://" + raw
        parsed = urlparse(raw)
        query_params = parse_qs(parsed.query)
        sku_id = query_params.get("skuId", [None])[0]
        clean_path = parsed.path

        # If skuId query param is absent, extract product ID from /p/{id}
        if not sku_id:
            p_match = re.search(r'/p/([a-zA-Z0-9_-]+)', clean_path)
            if p_match:
                sku_id = p_match.group(1)
            else:
                sku_id = clean_path.strip("/").split("/")[-1] or "nykaa_item"

        kept_params = {}
        if "skuId" in query_params:
            kept_params["skuId"] = query_params["skuId"][0]

        canonical_url = urlunparse(("https", "www.nykaa.com", clean_path, "", urlencode(kept_params), ""))
        return NormalizedURLResult(
            canonical_url=canonical_url,
            platform="nykaa",
            product_id=sku_id,
            variant_id=sku_id,
            original_url=url
        )

    @classmethod
    def normalize(cls, raw_url: str) -> NormalizedURLResult:
        """
        Dispatcher method: Detects platform and sanitizes URL accordingly.
        Supports shortlinks (amzn.in, amzn.to, a.co, fkrt.it, ajio.in) and URLs without scheme.
        """
        if not raw_url or not isinstance(raw_url, str):
            raise ValueError("Invalid URL provided")

        url = raw_url.strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        lower_url = url.lower()

        if "amazon." in lower_url or "amzn.in" in lower_url or "amzn.to" in lower_url or "a.co" in lower_url:
            return cls.normalize_amazon(url)
        elif "flipkart." in lower_url or "fkrt.it" in lower_url or "fkrt.co" in lower_url:
            return cls.normalize_flipkart(url)
        elif "myntra." in lower_url:
            return cls.normalize_myntra(url)
        elif "ajio." in lower_url:
            return cls.normalize_ajio(url)
        elif "nykaa." in lower_url:
            return cls.normalize_nykaa(url)
        else:
            raise ValueError(f"Unsupported e-commerce platform domain for URL: {raw_url}")
