"""
Platform Fetcher Service
========================
Dispatches URLs to modular store-specific scrapers (Amazon, Flipkart, Myntra, AJIO, Nykaa)
with Playwright dynamic rendering, multi-source extraction, and confidence validation.
"""

import re
import random
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from db.models import PlatformEnum, AvailabilityEnum
from core.config import settings
from scrapers import get_scraper_for_url, detect_store_platform, ExtractionResult

logger = logging.getLogger(__name__)


@dataclass
class ProductData:
    platform: PlatformEnum
    product_name: str
    product_url: str
    product_image: Optional[str] = None
    current_price: Optional[float] = None
    original_price: Optional[float] = None
    discount_percentage: Optional[float] = None
    rating: Optional[float] = None
    rating_count: Optional[int] = None
    review_count: Optional[int] = None
    currency: Optional[str] = "INR"
    availability: AvailabilityEnum = AvailabilityEnum.unknown
    description: Optional[str] = None
    error: Optional[str] = None
    success: bool = True
    variants: List[Dict[str, Any]] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    colors: List[Dict[str, Any]] = field(default_factory=list)
    observed_at: Optional[datetime] = None
    # Enhanced validation & debug fields
    store_product_id: Optional[str] = None
    confidence_score: int = 0
    status: str = "needs_verification"  # "verified", "needs_verification", "extraction_failed"
    debug_info: Optional[Dict[str, Any]] = None


def detect_platform(url: str) -> PlatformEnum:
    """Detect the e-commerce platform from a product URL."""
    return detect_store_platform(url)


async def async_fetch_product_data(url: str) -> ProductData:
    """
    Asynchronously fetch product data using dedicated store scrapers.
    """
    scraper, platform = get_scraper_for_url(url)

    if platform == PlatformEnum.unknown or not scraper:
        logger.warning(f"Unsupported store platform for URL: {url}")
        return ProductData(
            platform=PlatformEnum.unknown,
            product_name="",
            product_url=url,
            success=False,
            confidence_score=0,
            status="extraction_failed",
            error=(
                "Unsupported platform. We currently support Amazon India, Flipkart, AJIO, Myntra, and Nykaa. "
                "Please paste a valid product URL from one of these platforms."
            ),
        )

    product_id = scraper.extract_product_id(url)
    logger.info(f"Dispatching URL to {scraper.__class__.__name__} (Product ID: {product_id})")

    # Run extraction via store scraper
    result: ExtractionResult = await scraper.extract_product(url)

    debug_dict = None
    if result.debug_info:
        debug_dict = {
            "original_url": getattr(result.debug_info, "original_url", url),
            "normalized_url": getattr(result.debug_info, "normalized_url", url),
            "detected_store": getattr(result.debug_info, "detected_store", platform.value),
            "extracted_product_id": getattr(result.debug_info, "extracted_product_id", result.store_product_id),
            "candidate_prices": getattr(result.debug_info, "candidate_prices", []),
            "extraction_sources": getattr(result.debug_info, "extraction_sources", result.extraction_sources),
            "confidence_score": getattr(result.debug_info, "confidence_score", result.confidence_score),
            "status": getattr(result.debug_info, "status", result.status),
            "warnings": getattr(result.debug_info, "warnings", []),
        }

    # Print structured debug output to logs
    print_debug_summary(result)

    now = datetime.utcnow()
    if result.success and result.title and result.current_price is not None:
        return ProductData(
            platform=result.store,
            product_name=result.title,
            product_url=url,
            product_image=result.image_url,
            current_price=result.current_price,
            original_price=result.original_price,
            discount_percentage=result.discount_percentage,
            rating=result.rating,
            rating_count=result.rating_count,
            review_count=result.review_count,
            currency=result.currency or "INR",
            availability=result.availability,
            description=result.description or f"Verified product from {result.store.value.title()}",
            success=True,
            variants=result.variants,
            images=result.images or ([result.image_url] if result.image_url else []),
            colors=result.colors or [],
            observed_at=now,
            store_product_id=result.store_product_id,
            confidence_score=result.confidence_score,
            status=result.status,
            debug_info=debug_dict,
        )
    else:
        err_msg = result.error_message or "Unable to reliably extract verified product information from this page."
        return ProductData(
            platform=result.store,
            product_name=result.title or "",
            product_url=url,
            product_image=result.image_url,
            current_price=result.current_price,
            original_price=result.original_price,
            discount_percentage=result.discount_percentage,
            rating=result.rating,
            rating_count=result.rating_count,
            review_count=result.review_count,
            currency=result.currency or "INR",
            availability=result.availability,
            description=None,
            error=err_msg,
            success=False,
            variants=result.variants,
            observed_at=now,
            store_product_id=result.store_product_id,
            confidence_score=result.confidence_score,
            status="extraction_failed",
            debug_info=debug_dict,
        )


def fetch_product_data(url: str) -> ProductData:
    """
    Main synchronous entry point for fetching product data from a URL.
    Safely manages the async loop.
    """
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # If already inside an active event loop (e.g. Jupyter or certain frameworks), use run_until_complete or nest
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(async_fetch_product_data(url))
        else:
            return asyncio.run(async_fetch_product_data(url))
    except Exception as e:
        logger.error(f"Extraction error for {url}: {e}", exc_info=True)
        return ProductData(
            platform=detect_store_platform(url),
            product_name="",
            product_url=url,
            success=False,
            confidence_score=0,
            status="extraction_failed",
            error=f"Failed to fetch product data: {str(e)}",
        )


def fetch_updated_price(product_url: str, platform: PlatformEnum) -> Optional[ProductData]:
    """Fetch latest price for an existing product. Used by background Celery worker."""
    try:
        data = fetch_product_data(product_url)
        return data if data.success else None
    except Exception as e:
        logger.error(f"Price refresh failed for {product_url}: {e}")
        return None


def simulate_price_change(current_price: float, platform: PlatformEnum) -> float:
    """Simulate realistic price change for testing alert triggers."""
    change_pct = random.uniform(-0.15, 0.08)
    new_price = current_price * (1 + change_pct)
    return max(round(new_price, -1), 100.0)


def print_debug_summary(result: ExtractionResult):
    """Print clean diagnostic output to terminal/logs for debugging."""
    dbg = result.debug_info
    if not dbg:
        return

    logger.info("=" * 60)
    logger.info(f"PRODUCT EXTRACTION DIAGNOSTICS")
    logger.info("=" * 60)
    logger.info(f"Original URL:      {getattr(dbg, 'original_url', '')}")
    logger.info(f"Normalized URL:    {getattr(dbg, 'normalized_url', '')}")
    logger.info(f"Detected Store:    {getattr(dbg, 'detected_store', '')}")
    logger.info(f"Product ID:        {getattr(dbg, 'extracted_product_id', '')}")
    logger.info("-" * 60)
    candidate_prices = getattr(dbg, "candidate_prices", [])
    logger.info(f"Candidate Prices ({len(candidate_prices)}):")
    for p in candidate_prices:
        if isinstance(p, dict):
            logger.info(f"  - [{p.get('source')}] ₹{p.get('value')}")
    logger.info("-" * 60)
    logger.info(f"Final Selected Title: {result.title}")
    logger.info(f"Final Selected Price: ₹{result.current_price}")
    logger.info(f"Confidence Score:     {result.confidence_score}/100")
    logger.info(f"Status:               {result.status.upper()}")
    if hasattr(dbg, "warnings") and dbg.warnings:
        logger.info(f"Warnings:             {'; '.join(dbg.warnings)}")
    logger.info("=" * 60)
