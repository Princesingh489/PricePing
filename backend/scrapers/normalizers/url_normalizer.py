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
        parsed = urlparse(url.strip())
        netloc = "www.amazon.in" if "amazon" in parsed.netloc.lower() else parsed.netloc

        # Extract ASIN from path patterns: /dp/B0..., /gp/product/B0..., /gp/aw/d/B0...
        asin_match = re.search(r'/(?:dp|gp/product|gp/aw/d|product)/([A-Z0-9]{10})', parsed.path, re.IGNORECASE)
        asin = asin_match.group(1).upper() if asin_match else None

        # Check query parameters as fallback (e.g. ?asin=...)
        query_params = parse_qs(parsed.query)
        if not asin and "asin" in query_params:
            asin = query_params["asin"][0].upper()

        if not asin:
            raise ValueError(f"Could not identify a valid Amazon ASIN from URL: {url}")

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
        parsed = urlparse(url.strip())
        query_params = parse_qs(parsed.query)

        # 1. Extract PID (e.g., MOBFWBYZ8GAJ9F7F)
        pid = query_params.get("pid", [None])[0]
        if not pid:
            pid_match = re.search(r'[?&]pid=([A-Za-z0-9_-]+)', url)
            if pid_match:
                pid = pid_match.group(1)

        clean_path = parsed.path
        clean_path = re.sub(r'/+', '/', clean_path)

        kept_params = {}
        if pid:
            kept_params["pid"] = pid
        else:
            # Check for itm ID in path if PID query is missing
            itm_match = re.search(r'/p/(itm[a-zA-Z0-9]+)', clean_path)
            if not itm_match:
                raise ValueError(f"Cannot identify Flipkart product or variant PID from URL: {url}")
            pid = itm_match.group(1)
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
        parsed = urlparse(url.strip())
        path = parsed.path

        # Extract numeric Style ID from path
        style_match = re.search(r'/(\d{5,12})(?:/buy)?/?$', path)
        if not style_match:
            style_match = re.search(r'/(\d{5,12})', path)

        if not style_match:
            raise ValueError(f"Could not identify a valid Myntra Style ID from URL: {url}")

        style_id = style_match.group(1)

        # Standardize path ending with /buy
        base_path = re.sub(r'/\d{5,12}(?:/buy)?/?$', f'/{style_id}/buy', path)
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
        parsed = urlparse(url.strip())
        code_match = re.search(r'/p/([a-zA-Z0-9_-]+)', parsed.path)
        code = code_match.group(1) if code_match else None
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
        parsed = urlparse(url.strip())
        query_params = parse_qs(parsed.query)
        sku_id = query_params.get("skuId", [None])[0]
        clean_path = parsed.path
        kept_params = {}
        if sku_id:
            kept_params["skuId"] = sku_id
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
        """
        if not raw_url or not isinstance(raw_url, str):
            raise ValueError("Invalid URL provided")

        url = raw_url.strip()
        lower_url = url.lower()

        if "amazon." in lower_url:
            return cls.normalize_amazon(url)
        elif "flipkart." in lower_url:
            return cls.normalize_flipkart(url)
        elif "myntra." in lower_url:
            return cls.normalize_myntra(url)
        elif "ajio." in lower_url:
            return cls.normalize_ajio(url)
        elif "nykaa." in lower_url:
            return cls.normalize_nykaa(url)
        else:
            raise ValueError(f"Unsupported e-commerce platform domain for URL: {raw_url}")
