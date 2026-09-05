"""
Shared Models & Data Structures
================================
Defines unified data models for candidate extraction, field confidence, and extraction results.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
from db.models import PlatformEnum, AvailabilityEnum


@dataclass
class PriceCandidate:
    value: float
    source: str
    category: str  # "selling_price", "mrp", "coupon", "bank_offer", "emi", "exchange", "delivery", "related"
    confidence: int
    raw_text: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "source": self.source,
            "category": self.category,
            "confidence": self.confidence,
            "raw_text": self.raw_text,
        }


@dataclass
class FieldConfidence:
    title: int = 0
    current_price: int = 0
    original_price: int = 0
    discount: int = 0
    image: int = 0
    rating: int = 0
    variant: int = 0
    stock: int = 0
    overall: int = 0

    def to_dict(self) -> Dict[str, int]:
        return {
            "title": self.title,
            "current_price": self.current_price,
            "original_price": self.original_price,
            "discount": self.discount,
            "image": self.image,
            "rating": self.rating,
            "variant": self.variant,
            "stock": self.stock,
            "overall": self.overall,
        }


@dataclass
class ExtractionDebug:
    original_url: str
    normalized_url: str
    detected_store: str
    extracted_product_id: Optional[str] = None
    candidate_prices: List[Dict[str, Any]] = field(default_factory=list)
    candidate_titles: List[Dict[str, Any]] = field(default_factory=list)
    candidate_images: List[Dict[str, Any]] = field(default_factory=list)
    extraction_sources: Dict[str, str] = field(default_factory=dict)
    confidence_score: int = 0
    status: str = "pending"
    warnings: List[str] = field(default_factory=list)
    fetch_method: str = "fast_http"  # "fast_http", "playwright", "cached"


@dataclass
class ExtractionResult:
    store: PlatformEnum
    store_product_id: Optional[str]
    title: Optional[str] = None
    brand: Optional[str] = None
    current_price: Optional[float] = None
    original_price: Optional[float] = None
    discount_percentage: Optional[float] = None
    saved_amount: Optional[float] = None
    image_url: Optional[str] = None
    rating: Optional[float] = None
    rating_count: Optional[int] = None
    review_count: Optional[int] = None
    currency: str = "INR"
    availability: AvailabilityEnum = AvailabilityEnum.unknown
    variant: Optional[Dict[str, str]] = None
    variants: List[Dict[str, Any]] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    colors: List[Dict[str, Any]] = field(default_factory=list)
    canonical_url: Optional[str] = None
    description: Optional[str] = None
    confidence_score: int = 0
    field_confidence: Optional[FieldConfidence] = None
    status: str = "uncertain"  # "verified", "uncertain", "extraction_failed"
    extraction_sources: Dict[str, str] = field(default_factory=dict)
    debug_info: Optional[ExtractionDebug] = None
    success: bool = True
    error_message: Optional[str] = None
    product_url: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "platform": self.store.value if hasattr(self.store, 'value') else str(self.store),
            "store": self.store.value if hasattr(self.store, 'value') else str(self.store),
            "product_id": self.store_product_id,
            "store_product_id": self.store_product_id,
            "title": self.title,
            "brand": self.brand,
            "current_price": self.current_price,
            "price": self.current_price,
            "original_price": self.original_price,
            "mrp": self.original_price,
            "discount_percentage": self.discount_percentage,
            "discount": self.discount_percentage,
            "saved_amount": self.saved_amount,
            "you_save": self.saved_amount,
            "amount_saved": self.saved_amount,
            "image": self.image_url,
            "image_url": self.image_url,
            "product_image": self.image_url,
            "rating": self.rating,
            "rating_count": self.rating_count,
            "review_count": self.review_count,
            "currency": self.currency or "INR",
            "availability": self.availability.value if hasattr(self.availability, 'value') else str(self.availability),
            "variant": self.variant,
            "variants": self.variants,
            "images": self.images,
            "colors": self.colors,
            "canonical_url": self.canonical_url or self.product_url,
            "description": self.description,
            "confidence_score": self.confidence_score,
            "confidence": self.field_confidence.to_dict() if self.field_confidence else {"overall": self.confidence_score},
            "overall_confidence": self.confidence_score,
            "status": self.status,
            "success": self.success,
            "error": self.error_message,
            "error_message": self.error_message,
            "product_url": self.product_url,
            "url": self.product_url,
            "final_url": self.product_url,
            "extraction_sources": self.extraction_sources,
            "fetched_at": datetime.utcnow().isoformat() + "Z",
            "observed_at": datetime.utcnow().isoformat() + "Z",
        }

    def __getitem__(self, key: str) -> Any:
        return self.to_dict()[key]

    def __contains__(self, key: str) -> bool:
        return key in self.to_dict()

    def get(self, key: str, default: Any = None) -> Any:
        return self.to_dict().get(key, default)
