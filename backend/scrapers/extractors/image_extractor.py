"""
High-Resolution Product Image Extractor
=======================================
Extracts high-resolution main product gallery images with fallback chains (DOM gallery, dynamic zoom attributes, srcset, JSON-LD, OpenGraph) and placeholder filters.
"""
import re
import json
import logging
from urllib.parse import urljoin
from typing import Optional, List, Dict, Any
from bs4 import BeautifulSoup, Tag
from db.models import PlatformEnum

logger = logging.getLogger(__name__)


class ImageExtractor:
    # Invalid image keywords to reject
    INVALID_PATTERNS = [
        re.compile(r'placeholder', re.IGNORECASE),
        re.compile(r'spacer\.gif', re.IGNORECASE),
        re.compile(r'1x1', re.IGNORECASE),
        re.compile(r'logo', re.IGNORECASE),
        re.compile(r'icon', re.IGNORECASE),
        re.compile(r'banner', re.IGNORECASE),
        re.compile(r'data:image/svg\+xml', re.IGNORECASE),
    ]

    @classmethod
    def sanitize_image_url(cls, raw: Optional[str], base_url: str = "") -> Optional[str]:
        """Sanitize and validate an image URL."""
        if not raw:
            return None
        url = str(raw).strip()
        if not url:
            return None

        # Check rejection patterns
        for pat in cls.INVALID_PATTERNS:
            if pat.search(url):
                return None

        # Fix protocol-relative URLs
        if url.startswith("//"):
            url = "https:" + url
        elif url.startswith("/"):
            url = urljoin(base_url or "https://www.flipkart.com", url)

        # Must be valid HTTP(S) URL
        if not (url.startswith("http://") or url.startswith("https://")):
            return None

        return url

    @classmethod
    def normalize_flipkart_image(cls, raw_url: Optional[str], base_url: str = "") -> Optional[str]:
        """Upscale Flipkart thumbnail dimensions to high-resolution gallery image."""
        sanitized = cls.sanitize_image_url(raw_url, base_url)
        if not sanitized:
            return None

        # Upscale dimensions: /image/128/128/ -> /image/832/832/
        hires = re.sub(r'/image/\d+/\d+/', '/image/832/832/', sanitized)
        # Handle query params if any
        if "flixcart.com" in hires and "/image/" in hires:
            hires = re.sub(r'(\?|&)q=\d+', r'\1q=90', hires)
        return hires

    @classmethod
    def extract_largest_from_srcset(cls, srcset_str: str, base_url: str = "") -> Optional[str]:
        """Parse srcset attribute and pick the highest resolution image candidate."""
        if not srcset_str:
            return None
        parts = srcset_str.split(',')
        best_candidate = None
        max_width = 0

        for part in parts:
            part = part.strip()
            if not part:
                continue
            tokens = part.split()
            url_part = tokens[0]
            width = 0
            if len(tokens) > 1:
                w_match = re.search(r'(\d+)[wx]', tokens[1])
                if w_match:
                    width = int(w_match.group(1))
            if width > max_width or best_candidate is None:
                max_width = width
                best_candidate = url_part

        return cls.normalize_flipkart_image(best_candidate, base_url) if best_candidate else None

    @classmethod
    def extract_main_image(
        cls,
        soup: BeautifulSoup,
        container: Optional[Tag],
        platform: PlatformEnum,
        page_url: str = "",
        json_ld_data: Optional[Dict[str, Any]] = None,
        meta_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Multi-stage fallback chain for extracting the highest quality main product image.
        """
        target_container = container or soup

        # 1. Amazon high-resolution gallery
        if platform == PlatformEnum.amazon:
            landing_img = target_container.select_one('#landingImage, #imgBlkFront, #main-image')
            if landing_img:
                if landing_img.get('data-old-hires'):
                    s = cls.sanitize_image_url(landing_img['data-old-hires'], page_url)
                    if s:
                        return s
                if landing_img.get('data-a-dynamic-image'):
                    try:
                        dyn = json.loads(landing_img['data-a-dynamic-image'])
                        if isinstance(dyn, dict) and dyn:
                            sorted_imgs = sorted(dyn.items(), key=lambda x: x[1][0] if isinstance(x[1], list) and len(x[1]) > 0 else 0, reverse=True)
                            if sorted_imgs:
                                s = cls.sanitize_image_url(sorted_imgs[0][0], page_url)
                                if s:
                                    return s
                    except Exception:
                        pass
                if landing_img.get('src'):
                    s = cls.sanitize_image_url(landing_img['src'], page_url)
                    if s:
                        return s

        # 2. Flipkart gallery & srcset
        elif platform == PlatformEnum.flipkart:
            gallery_selectors = [
                'img.DByuf4', 'img._0DkuPH', 'img._396cs4._2amPTt', 'img._396cs4',
                'div.q61Yvd img', 'div.CXW8mj img', 'div._3kidBo img', 'img[src*="rukminim"]',
            ]
            for sel in gallery_selectors:
                img_elem = target_container.select_one(sel) or soup.select_one(sel)
                if img_elem:
                    srcset_val = img_elem.get('srcset') or img_elem.get('data-srcset')
                    if srcset_val:
                        hires = cls.extract_largest_from_srcset(srcset_val, page_url)
                        if hires:
                            return hires
                    for attr in ['src', 'data-src', 'data-lazy-src', 'data-original']:
                        raw_src = img_elem.get(attr)
                        if raw_src:
                            hires = cls.normalize_flipkart_image(raw_src, page_url)
                            if hires:
                                return hires

        # 3. Myntra gallery
        elif platform == PlatformEnum.myntra:
            img_elem = target_container.select_one('.image-grid-image, .image-grid-container img, .pdp-image img') or soup.select_one('.image-grid-image')
            if img_elem:
                raw_src = img_elem.get('src') or img_elem.get('style')
                if raw_src and 'url(' in raw_src:
                    m = re.search(r'url\(["\']?([^"\']+)["\']?\)', raw_src)
                    if m:
                        raw_src = m.group(1)
                s = cls.sanitize_image_url(raw_src, page_url)
                if s:
                    return s

        # 4. AJIO gallery
        elif platform == PlatformEnum.ajio:
            img_elem = target_container.select_one('.img-holder img, .preview-slider img, .rilrtl-lazy-img') or soup.select_one('.img-holder img')
            if img_elem:
                raw_src = img_elem.get('src') or img_elem.get('data-src')
                s = cls.sanitize_image_url(raw_src, page_url)
                if s:
                    return s

        # 5. Nykaa gallery
        elif platform == PlatformEnum.nykaa:
            img_elem = target_container.select_one('.css-1f6y8y8 img, .slider-container img, .main-product-image') or soup.select_one('.main-product-image img')
            if img_elem:
                raw_src = img_elem.get('src') or img_elem.get('data-src')
                s = cls.sanitize_image_url(raw_src, page_url)
                if s:
                    return s

        # 6. JSON-LD Fallback
        if json_ld_data and json_ld_data.get("image"):
            s = cls.sanitize_image_url(json_ld_data["image"], page_url)
            if s:
                return s

        # 7. Meta Fallback
        if meta_data and meta_data.get("image"):
            s = cls.sanitize_image_url(meta_data["image"], page_url)
            if s:
                return s

        return None
