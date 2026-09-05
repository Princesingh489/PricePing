"""
DOM Scoping and Element Extractor
================================
Scopes extraction strictly to the main product detail container, rejecting recommended, related, and sponsored product sections.
"""
import re
from typing import Optional, List, Tuple
from bs4 import BeautifulSoup, Tag
from db.models import PlatformEnum, AvailabilityEnum


class DomExtractor:
    # Store-specific main product container selectors
    MAIN_CONTAINERS = {
        PlatformEnum.amazon: [
            "#dp-container",
            "#ppd",
            "#centerCol",
            "#desktop_buybox",
        ],
        PlatformEnum.flipkart: [
            "div.DOjaWF.YJG4Cf",
            "div.DOjaWF",
            "div._1YokD2._3Mn1Gg",
            "div._1YokD2",
            "div.cPHDOP",
            "div.t-0M7P",
        ],
        PlatformEnum.myntra: [
            "div.pdp-details",
            "div.pdp-description-container",
            "div.pdp-container",
        ],
        PlatformEnum.ajio: [
            "div.prod-content",
            "div.prod-container",
            "div.product-details",
        ],
        PlatformEnum.nykaa: [
            "div.product-details",
            "div.css-11v5k9",
            "div.css-1e5x64",
            "div.product-des-container",
        ],
    }

    # Suffixes to clean from page titles
    TITLE_CLEAN_PATTERNS = [
        re.compile(r'\s*:\s*Buy\s+Online.*$', re.IGNORECASE),
        re.compile(r'\s*:\s*Amazon\.in.*$', re.IGNORECASE),
        re.compile(r'\s*-\s*Flipkart\.com.*$', re.IGNORECASE),
        re.compile(r'\s*\|\s*Flipkart.*$', re.IGNORECASE),
        re.compile(r'\s*-\s*Buy.*Online\s+at\s+Myntra.*$', re.IGNORECASE),
        re.compile(r'\s*-\s*Buy.*Online\s+at\s+AJIO.*$', re.IGNORECASE),
        re.compile(r'\s*-\s*Nykaa.*$', re.IGNORECASE),
        re.compile(r'\s*\|\s*Nykaa.*$', re.IGNORECASE),
    ]

    @classmethod
    def get_main_container(cls, soup: BeautifulSoup, platform: PlatformEnum) -> Optional[Tag]:
        """Scope soup to the main product detail container."""
        selectors = cls.MAIN_CONTAINERS.get(platform, [])
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem
        return None

    GENERIC_NOISE_TITLES = [
        "amazon product page", "amazon.in", "flipkart.com", "online shopping", "myntra", "ajio", "nykaa",
        "404 not found", "access denied", "page not found"
    ]

    @classmethod
    def clean_title(cls, raw: Optional[str]) -> Optional[str]:
        """Clean raw product title by removing website noise and excessive whitespace."""
        if not raw:
            return None
        text = " ".join(raw.split())
        for pattern in cls.TITLE_CLEAN_PATTERNS:
            text = pattern.sub('', text).strip()
        if text.lower() in cls.GENERIC_NOISE_TITLES:
            return None
        return text if len(text) >= 3 else None

    @classmethod
    def extract_availability(cls, container: Tag | BeautifulSoup, platform: PlatformEnum) -> AvailabilityEnum:
        """Extract stock availability from main product container."""
        text = container.get_text().lower() if container else ""

        # Check out of stock triggers
        out_triggers = [
            "currently unavailable",
            "out of stock",
            "sold out",
            "temporarily unavailable",
            "item is unavailable",
        ]
        for trigger in out_triggers:
            if trigger in text:
                return AvailabilityEnum.out_of_stock

        # Check low stock triggers
        if re.search(r'only\s+\d+\s+left\s+in\s+stock', text, re.IGNORECASE):
            return AvailabilityEnum.low_stock

        return AvailabilityEnum.in_stock
