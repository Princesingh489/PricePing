from ecommerce.registry import registry, ALL_SUPPORTED_STORES
from ecommerce.base_adapter import BaseEcommerceAdapter
from ecommerce.product_matcher import extract_specs, is_strict_match

__all__ = [
    "registry",
    "ALL_SUPPORTED_STORES",
    "BaseEcommerceAdapter",
    "extract_specs",
    "is_strict_match",
]
