"""
Ecommerce Store Registry & Multi-Store Aggregator
=================================================
Central registry for all store adapters with parallel asynchronous cross-store searching,
fail-safe independent execution, and guaranteed multi-store comparison matrix.
"""

from datetime import datetime, timezone
import asyncio
import logging
from typing import Optional, Dict, Any, List

from ecommerce.base_adapter import BaseEcommerceAdapter
from ecommerce.amazon_adapter import AmazonAdapter
from ecommerce.flipkart_adapter import FlipkartAdapter
from ecommerce.myntra_adapter import MyntraAdapter
from ecommerce.ajio_adapter import AjioAdapter
from ecommerce.nykaa_adapter import NykaaAdapter
from core.config import settings

logger = logging.getLogger(__name__)

ALL_SUPPORTED_STORES = [
    {"store": "amazon", "name": "Amazon India", "logo": "amazon", "default_domain": "amazon.in"},
    {"store": "flipkart", "name": "Flipkart", "logo": "flipkart", "default_domain": "flipkart.com"},
    {"store": "myntra", "name": "Myntra", "logo": "myntra", "default_domain": "myntra.com"},
    {"store": "ajio", "name": "AJIO", "logo": "ajio", "default_domain": "ajio.com"},
    {"store": "nykaa", "name": "Nykaa", "logo": "nykaa", "default_domain": "nykaa.com"},
]


from services.canonical_service import CanonicalService
from services.availability_checker import AvailabilityChecker
from services.product_matcher import ProductMatchingEngine
from services.product_normalizer import ProductNormalizer


class EcommerceRegistry:
    def __init__(self):
        self._adapters: Dict[str, BaseEcommerceAdapter] = {
            "amazon": AmazonAdapter(),
            "flipkart": FlipkartAdapter(),
            "myntra": MyntraAdapter(),
            "ajio": AjioAdapter(),
            "nykaa": NykaaAdapter(),
        }

    def get_adapter_by_store(self, store: str) -> Optional[BaseEcommerceAdapter]:
        if not store:
            return None
        return self._adapters.get(store.lower())

    def get_adapter_by_url(self, url: str) -> Optional[BaseEcommerceAdapter]:
        if not url:
            return None
        for adapter in self._adapters.values():
            if adapter.detect_url(url):
                return adapter
        return None

    def detect_store_from_url(self, url: str) -> str:
        adapter = self.get_adapter_by_url(url)
        return adapter.store_name if adapter else "unknown"

    def get_canonical_product(self, base_product: Dict[str, Any]) -> Dict[str, Any]:
        """Generate deterministic internal canonical product identity."""
        return CanonicalService.create_canonical_product(base_product)

    def get_five_stores_summary(self, comparison_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compute the 5-store availability summary."""
        return AvailabilityChecker.calculate_five_stores_summary(comparison_list)

    async def fetch_cross_store_comparison(
        self,
        base_product: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Produce a comparison list across ALL 5 supported stores:
        Amazon, Flipkart, Myntra, AJIO, Nykaa.

        Enforces strict Product Identity -> Variant -> Availability -> Price Pipeline:
        - Origin store uses verified base data.
        - Other 4 stores run concurrent multi-candidate searches.
        - Enforces hard conflicts (brand, model, storage, RAM, size, color, pack).
        - Separates product match from variant match and variant availability.
        - Never guesses or uses weak title similarity to claim an exact match.
        """
        origin_store = (base_product.get("store") or "unknown").lower()
        title = base_product.get("title") or ""
        brand = base_product.get("brand")
        model = base_product.get("model")
        variant = base_product.get("variant")

        canonical_prod = CanonicalService.create_canonical_product(base_product)

        now_iso = datetime.now(timezone.utc).isoformat()
        origin_observed = base_product.get("observed_at") or now_iso

        offers_by_store: Dict[str, Dict[str, Any]] = {}

        # 1. Populate origin store offer
        if origin_store in self._adapters:
            origin_price = base_product.get("price")
            origin_avail = base_product.get("availability") or "in_stock"
            is_in_stock = origin_avail == "in_stock" and origin_price is not None

            origin_audit = {
                "brand_match": True,
                "model_match": True,
                "gtin_match": True if base_product.get("gtin") else None,
                "color_match": True if canonical_prod.get("color") else None,
                "size_match": True if canonical_prod.get("size") else None,
                "storage_match": True if canonical_prod.get("storage") else None,
                "ram_match": True if canonical_prod.get("ram") else None,
                "title_similarity": 1.0,
                "variant_match": True,
                "match_confidence": 1.0,
                "match_reason": "Original user submitted listing (verified)",
            }

            badge = "✓ Verified Match" if is_in_stock else "✓ Verified Match (Out of Stock)"

            offers_by_store[origin_store] = {
                "store": origin_store,
                "seller_name": base_product.get("seller") or f"{origin_store.title()} Verified",
                "price": origin_price,
                "original_price": base_product.get("original_price"),
                "shipping_price": 0.0,
                "delivery_text": "Fast Store Delivery",
                "coupon_text": "Verified Active Price",
                "url": base_product.get("url"),
                "availability": origin_avail,
                "external_product_id": base_product.get("product_id"),
                "is_verified_match": True,
                "match_status": "verified_match",
                "status": "available" if is_in_stock else "unavailable",
                "match_confidence": 1.0,
                "match_signals": origin_audit,
                "audit": origin_audit,
                "match_reason": "Original store listing match",
                "badge_label": badge,
                "is_purchasable": is_in_stock,
                "variants": base_product.get("variants") or [],
                "observed_at": origin_observed,
            }

        # 2. Search other stores concurrently if enabled
        if settings.CROSS_STORE_SEARCH_ENABLED and title:
            from ecommerce.product_matcher import extract_specs
            specs = extract_specs(title, brand=brand)
            eff_brand = specs.get("brand") or brand or canonical_prod.get("brand")
            eff_model = specs.get("model") or model or canonical_prod.get("model")
            eff_variant = specs.get("size") or variant or specs.get("storage") or canonical_prod.get("size") or canonical_prod.get("storage")

            tasks = []
            stores_to_search = [s for s in self._adapters.keys() if s != origin_store]

            async def query_store(store_key: str):
                adapter = self._adapters[store_key]
                try:
                    # Parallel targeted candidate query with timeout
                    res = await asyncio.wait_for(
                        adapter.search_matching_product(
                            title=title,
                            brand=eff_brand,
                            model=eff_model,
                            variant=eff_variant,
                        ),
                        timeout=3.5
                    )
                    return store_key, res
                except Exception as e:
                    logger.debug(f"Store search failed for {store_key}: {e}")
                    return store_key, None

            for s in stores_to_search:
                tasks.append(query_store(s))

            results = await asyncio.gather(*tasks, return_exceptions=True)
            for res in results:
                if isinstance(res, tuple) and len(res) == 2:
                    store_key, offer_data = res
                    if offer_data:
                        offers_by_store[store_key] = offer_data

        # 3. Assemble complete standardized list for ALL 5 stores
        comparison_list = []
        for info in ALL_SUPPORTED_STORES:
            st = info["store"]
            matched_offer = offers_by_store.get(st)

            if matched_offer and matched_offer.get("is_verified_match") and matched_offer.get("price") is not None:
                avail = matched_offer.get("availability") or "in_stock"
                is_in_stock = avail == "in_stock"
                badge = "✓ Verified Match" if is_in_stock else "✓ Verified Match (Out of Stock)"
                comparison_list.append({
                    "store": st,
                    "store_name": info["name"],
                    "logo": info["logo"],
                    "price": matched_offer["price"],
                    "original_price": matched_offer.get("original_price"),
                    "shipping_price": matched_offer.get("shipping_price", 0.0),
                    "delivery_text": matched_offer.get("delivery_text") or "Standard Delivery",
                    "coupon_text": matched_offer.get("coupon_text"),
                    "url": matched_offer.get("url") or f"https://www.{info['default_domain']}",
                    "availability": avail,
                    "is_verified_match": True,
                    "match_status": "verified_match",
                    "status": "available" if is_in_stock else "unavailable",
                    "match_confidence": matched_offer.get("match_confidence", 1.0),
                    "match_signals": matched_offer.get("match_signals") or matched_offer.get("audit"),
                    "audit": matched_offer.get("audit") or matched_offer.get("match_signals"),
                    "match_reason": matched_offer.get("match_reason") or "Verified match",
                    "badge_label": badge,
                    "is_purchasable": is_in_stock,
                    "variants": matched_offer.get("variants") or [],
                    "observed_at": matched_offer.get("observed_at") or now_iso,
                })
            elif matched_offer and (matched_offer.get("match_status") == "possible_match" or (matched_offer.get("match_confidence", 0.0) >= 0.75 and not matched_offer.get("is_verified_match"))):
                comparison_list.append({
                    "store": st,
                    "store_name": info["name"],
                    "logo": info["logo"],
                    "price": matched_offer.get("price"),
                    "original_price": matched_offer.get("original_price"),
                    "shipping_price": matched_offer.get("shipping_price", 0.0),
                    "delivery_text": "Inconclusive Verification",
                    "coupon_text": None,
                    "url": matched_offer.get("url") or f"https://www.{info['default_domain']}",
                    "availability": matched_offer.get("availability") or "unavailable",
                    "is_verified_match": False,
                    "match_status": "possible_match",
                    "status": "unavailable",
                    "match_confidence": matched_offer.get("match_confidence", 0.80),
                    "match_signals": matched_offer.get("match_signals") or matched_offer.get("audit"),
                    "audit": matched_offer.get("audit") or matched_offer.get("match_signals"),
                    "match_reason": matched_offer.get("match_reason") or "? Possible match (Product looks similar, verification inconclusive)",
                    "badge_label": "? Possible Match",
                    "is_purchasable": False,
                    "variants": [],
                    "observed_at": matched_offer.get("observed_at") or now_iso,
                })
            elif matched_offer and matched_offer.get("status") == "no_match":
                comparison_list.append({
                    "store": st,
                    "store_name": info["name"],
                    "logo": info["logo"],
                    "price": None,
                    "original_price": None,
                    "shipping_price": 0.0,
                    "delivery_text": "Not Available",
                    "coupon_text": None,
                    "url": matched_offer.get("url") or f"https://www.{info['default_domain']}",
                    "availability": "unavailable",
                    "is_verified_match": False,
                    "match_status": "no_verified_match",
                    "status": "no_match",
                    "match_confidence": matched_offer.get("match_confidence", 0.0),
                    "match_signals": matched_offer.get("match_signals") or matched_offer.get("audit"),
                    "audit": matched_offer.get("audit") or matched_offer.get("match_signals"),
                    "match_reason": matched_offer.get("match_reason") or "— No exact verified match found",
                    "badge_label": "— No Verified Match",
                    "is_purchasable": False,
                    "variants": [],
                    "observed_at": matched_offer.get("observed_at") or now_iso,
                })
            else:
                comparison_list.append({
                    "store": st,
                    "store_name": info["name"],
                    "logo": info["logo"],
                    "price": None,
                    "original_price": None,
                    "shipping_price": 0.0,
                    "delivery_text": "Not Available",
                    "coupon_text": None,
                    "url": f"https://www.{info['default_domain']}",
                    "availability": "unavailable",
                    "is_verified_match": False,
                    "match_status": "no_verified_match",
                    "status": "no_match",
                    "match_confidence": 0.0,
                    "match_signals": None,
                    "audit": None,
                    "match_reason": "— Store search timed out or returned no reliable candidates",
                    "badge_label": "— No Verified Match",
                    "is_purchasable": False,
                    "variants": [],
                    "observed_at": now_iso,
                })

        return comparison_list


# Singleton registry instance
registry = EcommerceRegistry()

