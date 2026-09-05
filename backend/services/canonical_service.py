"""
PricePing Canonical Product Service
===================================
Constructs deterministic internal canonical product identities (CP-XXXXXX)
and links marketplace product offers under a universal product representation.
Enforces Step 3 & Step 26.
"""
import hashlib
from typing import Optional, Dict, Any, List
from services.product_normalizer import ProductNormalizer


class CanonicalService:
    """Manages universal Canonical Product identities and schema mapping."""

    @staticmethod
    def generate_canonical_id(
        brand: Optional[str],
        title: str,
        model: Optional[str] = None,
        category: Optional[str] = None,
        variant_specs: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate a deterministic internal canonical product ID (e.g. 'CP-8A92F1').
        Uses SHA-256 hash of normalized brand + model/core tokens + variant specs.
        """
        norm_b = ProductNormalizer.normalize_brand(brand) or "generic"
        norm_m = (model or "").lower().strip()
        norm_cat = (category or "").lower().strip()

        v_tokens = []
        if variant_specs:
            for k in sorted(variant_specs.keys()):
                val = variant_specs[k]
                if val:
                    v_tokens.append(f"{k}:{str(val).lower().strip()}")

        seed = f"{norm_b}|{norm_m or title[:50].lower()}|{norm_cat}|{'-'.join(v_tokens)}"
        hash_hex = hashlib.sha256(seed.encode("utf-8")).hexdigest().upper()
        return f"CP-{hash_hex[:6]}"

    @classmethod
    def create_canonical_product(
        cls,
        product_or_title: Any = None,
        brand: Optional[str] = None,
        model: Optional[str] = None,
        mpn: Optional[str] = None,
        gtin: Optional[str] = None,
        ean: Optional[str] = None,
        upc: Optional[str] = None,
        category: Optional[str] = None,
        color: Optional[str] = None,
        size: Optional[str] = None,
        storage: Optional[str] = None,
        ram: Optional[str] = None,
        pack_count: int = 1,
        images: Optional[List[str]] = None,
        attributes: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Build standard Canonical Product schema (Step 26).
        Accepts a product dictionary or individual keyword arguments.
        """
        if isinstance(product_or_title, dict):
            d = product_or_title
            title = d.get("title") or d.get("product_name") or ""
            brand = brand or d.get("brand")
            model = model or d.get("model")
            mpn = mpn or d.get("mpn")
            gtin = gtin or d.get("gtin")
            ean = ean or d.get("ean")
            upc = upc or d.get("upc")
            category = category or d.get("category")
            color = color or d.get("color")
            size = size or d.get("size")
            storage = storage or d.get("storage")
            ram = ram or d.get("ram")
            pack_count = d.get("pack_count") or pack_count or 1
            images = images or d.get("images") or ([d["image_url"]] if d.get("image_url") else [])
            attributes = attributes or d.get("attributes") or {}
        else:
            title = str(product_or_title or kwargs.get("title") or "")
            brand = brand or kwargs.get("brand")
            model = model or kwargs.get("model")
            mpn = mpn or kwargs.get("mpn")
            gtin = gtin or kwargs.get("gtin")
            ean = ean or kwargs.get("ean")
            upc = upc or kwargs.get("upc")
            category = category or kwargs.get("category")
            color = color or kwargs.get("color")
            size = size or kwargs.get("size")
            storage = storage or kwargs.get("storage")
            ram = ram or kwargs.get("ram")
            pack_count = kwargs.get("pack_count") or pack_count or 1
            images = images or kwargs.get("images") or []
            attributes = attributes or kwargs.get("attributes") or {}

        specs = {
            "color": ProductNormalizer.normalize_color(color),
            "size": ProductNormalizer.normalize_size(size),
            "storage": ProductNormalizer.normalize_storage(storage),
            "ram": ProductNormalizer.normalize_ram(ram),
            "pack_count": pack_count,
        }

        canonical_id = cls.generate_canonical_id(
            brand=brand,
            title=title,
            model=model,
            category=category,
            variant_specs=specs,
        )


        return {
            "canonical_product_id": canonical_id,
            "brand": ProductNormalizer.normalize_brand(brand),
            "product_name": title,
            "category": category or "general",
            "model": model,
            "mpn": mpn,
            "gtin": gtin,
            "ean": ean,
            "upc": upc,
            "color": specs["color"],
            "size": specs["size"],
            "storage": specs["storage"],
            "ram": specs["ram"],
            "pack_count": pack_count,
            "images": images or [],
            "attributes": attributes or {},
        }
