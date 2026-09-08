from pydantic import BaseModel, EmailStr, HttpUrl, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from db.models import (
    PlatformEnum, AvailabilityEnum, TrackingStatusEnum,
    AlertTypeEnum, AlertStatusEnum, NotificationTypeEnum, NotificationStatusEnum
)


# ---- Auth Schemas ----

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone_number: Optional[str] = None

    @validator("password")
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    phone_number: Optional[str]
    is_admin: bool
    email_notifications: bool
    push_notifications: bool
    sms_notifications: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None


class ForgotPassword(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    token: str
    new_password: str

    @validator("new_password")
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class GoogleAuthRequest(BaseModel):
    code: Optional[str] = None
    redirect_uri: Optional[str] = None
    credential: Optional[str] = None


# ---- Product Schemas ----

class ProductCreate(BaseModel):
    url: Optional[str] = None
    product_url: Optional[str] = None
    target_price: Optional[float] = None
    target_min_price: Optional[float] = None
    target_max_price: Optional[float] = None
    product_name: Optional[str] = None
    current_price: Optional[float] = None
    original_price: Optional[float] = None
    discount_percentage: Optional[float] = None
    product_image: Optional[str] = None
    image_url: Optional[str] = None
    rating: Optional[float] = None
    rating_count: Optional[int] = None
    brand: Optional[str] = None
    store: Optional[str] = None

    def get_url(self) -> str:
        u = self.url or self.product_url
        if not u:
            raise ValueError("URL is required (use 'url' or 'product_url')")
        return u.strip()


class ColorSwatchOut(BaseModel):
    name: str
    thumbnail: Optional[str] = None
    price: Optional[float] = None
    mrp: Optional[float] = None
    in_stock: bool = True
    product_url: Optional[str] = None


class ProductVariantOut(BaseModel):
    size: Optional[str] = None
    color: Optional[str] = None
    color_thumbnail: Optional[str] = None
    price: float
    mrp: Optional[float] = None
    discount_percentage: Optional[float] = None
    in_stock: bool = True
    sku: Optional[str] = None
    product_url: Optional[str] = None


class ProductOut(BaseModel):
    id: int
    platform: PlatformEnum
    store: Optional[str] = None
    external_product_id: Optional[str] = None
    canonical_id: Optional[str] = None
    product_name: str
    title: Optional[str] = None
    product_url: str
    canonical_url: Optional[str] = None
    product_image: Optional[str]
    image_url: Optional[str] = None
    images: Optional[List[str]] = []
    brand: Optional[str] = None
    model: Optional[str] = None
    variant: Optional[str] = None
    selected_color: Optional[str] = None
    selected_size: Optional[str] = None
    colors: Optional[List[ColorSwatchOut]] = []
    variants: Optional[List[ProductVariantOut]] = []
    current_price: Optional[float]
    original_price: Optional[float]
    discount_percentage: Optional[float]
    saved_amount: Optional[float] = None
    lowest_price: Optional[float]
    highest_price: Optional[float]
    average_price: Optional[float] = None
    history_state: Optional[str] = "ORGANIC_COLD_START"
    rating: Optional[float] = None
    rating_count: Optional[int] = None
    review_count: Optional[int] = None
    currency: Optional[str] = "INR"
    availability: Optional[AvailabilityEnum] = AvailabilityEnum.in_stock
    status: Optional[str] = "PENDING"
    observed_at: Optional[datetime] = None
    last_checked: Optional[datetime] = None
    created_at: Optional[datetime] = None

    @validator("availability", pre=True, always=True)
    def default_availability(cls, v):
        return v or AvailabilityEnum.in_stock

    class Config:
        from_attributes = True


class ProductPendingResponse(BaseModel):
    product_id: int
    status: str = "pending"
    canonical_url: str
    platform: str
    message: str


class TrackedProductAlertOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    alert_type: AlertTypeEnum
    target_price: Optional[float] = None
    minimum_price: Optional[float] = None
    maximum_price: Optional[float] = None
    percentage_drop: Optional[float] = None
    base_price: Optional[float] = None
    alert_status: AlertStatusEnum
    notify_email: bool = True
    notify_push: bool = True
    notify_sms: bool = False
    notify_in_app: bool = True
    last_triggered_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TrackedProductOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    tracking_status: TrackingStatusEnum
    target_min_price: Optional[float]
    target_max_price: Optional[float]
    notes: Optional[str]
    created_at: datetime
    tracked_at: Optional[datetime] = None
    product: ProductOut
    alert: Optional[TrackedProductAlertOut] = None

    class Config:
        from_attributes = True


class TrackedProductsResponse(BaseModel):
    items: List[TrackedProductOut]
    total: int


class TrackedProductUpdate(BaseModel):
    tracking_status: Optional[TrackingStatusEnum] = None
    target_min_price: Optional[float] = None
    target_max_price: Optional[float] = None
    notes: Optional[str] = None


# ---- Price History & Comparison Schemas ----

class PriceHistoryOut(BaseModel):
    id: int
    product_id: int
    store: Optional[str] = None
    price: float
    original_price: Optional[float]
    currency: Optional[str] = "INR"
    availability: AvailabilityEnum
    source: Optional[str] = "priceping_observation"
    verified: Optional[bool] = True
    checked_at: datetime

    class Config:
        from_attributes = True


# ---- Canonical Product & Exact Identity Comparison Schemas ----

class MatchAuditOut(BaseModel):
    model_config = {"protected_namespaces": ()}
    brand_match: Optional[bool] = None
    model_match: Optional[bool] = None
    gtin_match: Optional[bool] = None
    color_match: Optional[bool] = None
    size_match: Optional[bool] = None
    storage_match: Optional[bool] = None
    ram_match: Optional[bool] = None
    title_similarity: Optional[float] = 0.0
    variant_match: Optional[bool] = None
    match_confidence: Optional[float] = 0.0
    match_reason: Optional[str] = None


class CanonicalProductOut(BaseModel):
    canonical_product_id: str
    brand: Optional[str] = None
    product_name: Optional[str] = None
    category: Optional[str] = None
    model: Optional[str] = None
    mpn: Optional[str] = None
    gtin: Optional[str] = None
    ean: Optional[str] = None
    upc: Optional[str] = None
    gender: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    storage: Optional[str] = None
    ram: Optional[str] = None
    pack_count: Optional[int] = 1
    images: Optional[List[str]] = []
    attributes: Optional[Dict[str, Any]] = {}


class FiveStoresAvailabilitySummary(BaseModel):
    all_available: bool = False
    available_count: int = 0
    total_stores: int = 5
    verified_match_count: int = 0
    message: str = "Available on 1 of 5 stores"
    status: str = "partially_available"  # all_available | partially_available | unavailable


class StoreOfferOut(BaseModel):
    store: str
    store_name: str
    logo: str
    price: Optional[float] = None
    original_price: Optional[float] = None
    shipping_price: float = 0.0
    delivery_text: Optional[str] = None
    coupon_text: Optional[str] = None
    url: Optional[str] = None
    availability: str  # in_stock | out_of_stock | unavailable
    is_verified_match: bool = True
    match_status: str = "verified_match"  # verified_match | possible_match | no_verified_match
    status: str = "available"  # available | unavailable | pending | no_match
    match_confidence: Optional[float] = None
    match_signals: Optional[Dict[str, Any]] = None
    audit: Optional[Dict[str, Any]] = None
    match_reason: Optional[str] = None
    badge_label: Optional[str] = None
    is_purchasable: bool = True
    variants: Optional[List[ProductVariantOut]] = []
    observed_at: Optional[datetime] = None


class CrossStoreComparisonResponse(BaseModel):
    product_id: int
    product_name: str
    canonical_product: Optional[CanonicalProductOut] = None
    availability_summary: Optional[FiveStoresAvailabilitySummary] = None
    lowest_store: Optional[str] = None
    lowest_price: Optional[float] = None
    highest_price: Optional[float] = None
    max_savings: Optional[float] = None
    stores: List[StoreOfferOut]


class StorePriceHistoryPoint(BaseModel):
    timestamp: str
    date: str
    price: float
    original_price: Optional[float] = None
    store: str
    source: str
    availability: str


class RealPriceStatisticsOut(BaseModel):
    current_price: Optional[float]
    highest_price: Optional[float]
    lowest_price: Optional[float]
    average_price: Optional[float]
    median_price: Optional[float]
    price_change: Optional[float]
    percentage_change: Optional[float]
    potential_saving: Optional[float] = 0.0
    lowest_price_date: Optional[str] = None
    highest_price_date: Optional[str] = None
    days_since_lowest: Optional[int] = None
    days_since_highest: Optional[int] = None
    observation_count: int
    is_reliable: bool
    recommendation: str
    recommendation_reason: str


class RealPriceHistoryResponse(BaseModel):
    product_id: int
    store: str
    currency: str = "INR"
    history_start_date: Optional[str] = None
    history_end_date: Optional[str] = None
    observation_count: int = 0
    source: str = "priceping_observation"
    has_history: bool = False
    coverage_label: str
    data: List[StorePriceHistoryPoint] = []
    store_histories: Optional[dict] = {}
    statistics: Optional[RealPriceStatisticsOut] = None


# ---- Product Detail & Statistics Schemas ----

class PriceStatsOut(BaseModel):
    lowest_ever: Optional[float]
    highest_ever: Optional[float]
    average_price: Optional[float]
    data_points: int
    tracking_days: int


class DealScoreOut(BaseModel):
    recommendation: str  # BUY_NOW | WAIT | WATCH | INSUFFICIENT_DATA | FAIR_PRICE
    confidence: int
    percentile: Optional[float]
    avg_price: Optional[float]
    lowest_price: Optional[float]
    highest_price: Optional[float]
    data_points: int
    tracking_days: int
    message: str


class ProductDetailOut(BaseModel):
    tracker_id: int
    product: ProductOut
    price_history: List[PriceHistoryOut]
    deal_score: DealScoreOut
    stats: PriceStatsOut
    real_statistics: Optional[RealPriceStatisticsOut] = None
    cross_store_offers: Optional[List[StoreOfferOut]] = []
    history_metadata: Optional[dict] = None
    existing_alert: Optional["AlertOut"] = None

    class Config:
        from_attributes = True


class ResolveUrlRequest(BaseModel):
    product_url: str


class ResolveUrlResponse(BaseModel):
    detected_store: str
    extracted_product_id: Optional[str] = None
    product: ProductOut
    canonical_product: Optional[CanonicalProductOut] = None
    comparison: List[StoreOfferOut]
    availability_summary: Optional[FiveStoresAvailabilitySummary] = None
    statistics: RealPriceStatisticsOut
    history_summary: dict
    is_already_tracked: bool = False
    tracker_id: Optional[int] = None
    search_status: Optional[str] = "completed"


# ---- Alert Schemas ----

class AlertCreate(BaseModel):
    product_id: int
    alert_type: AlertTypeEnum
    target_price: Optional[float] = None
    minimum_price: Optional[float] = None
    maximum_price: Optional[float] = None
    percentage_drop: Optional[float] = None
    notify_email: bool = True
    notify_push: bool = True
    notify_sms: bool = False
    notify_in_app: bool = True

    @validator("target_price", always=True)
    def validate_target_price(cls, v, values):
        if values.get("alert_type") == AlertTypeEnum.below_price and v is None:
            raise ValueError("target_price is required for below_price alert type")
        return v

    @validator("minimum_price", always=True)
    def validate_min_price(cls, v, values):
        if values.get("alert_type") == AlertTypeEnum.price_range and v is None:
            raise ValueError("minimum_price is required for price_range alert type")
        return v

    @validator("maximum_price", always=True)
    def validate_max_price(cls, v, values):
        if values.get("alert_type") == AlertTypeEnum.price_range and v is None:
            raise ValueError("maximum_price is required for price_range alert type")
        return v

    @validator("percentage_drop", always=True)
    def validate_percentage_drop(cls, v, values):
        if values.get("alert_type") == AlertTypeEnum.percentage_drop and v is None:
            raise ValueError("percentage_drop is required for percentage_drop alert type")
        return v


class AlertOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    alert_type: AlertTypeEnum
    target_price: Optional[float]
    minimum_price: Optional[float]
    maximum_price: Optional[float]
    percentage_drop: Optional[float]
    base_price: Optional[float]
    alert_status: AlertStatusEnum
    notify_email: bool
    notify_push: bool
    notify_sms: bool
    notify_in_app: bool
    last_triggered_at: Optional[datetime]
    created_at: datetime
    product: ProductOut

    class Config:
        from_attributes = True


class AlertUpdate(BaseModel):
    target_price: Optional[float] = None
    minimum_price: Optional[float] = None
    maximum_price: Optional[float] = None
    percentage_drop: Optional[float] = None
    alert_status: Optional[AlertStatusEnum] = None
    notify_email: Optional[bool] = None
    notify_push: Optional[bool] = None
    notify_sms: Optional[bool] = None
    notify_in_app: Optional[bool] = None


# ---- Notification Schemas ----

class NotificationOut(BaseModel):
    id: int
    user_id: int
    product_id: Optional[int]
    notification_type: NotificationTypeEnum
    title: str
    message: str
    status: NotificationStatusEnum
    sent_at: Optional[datetime]
    read_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ---- Admin Schemas ----

class AdminStats(BaseModel):
    total_users: int
    total_products: int
    total_tracked: int
    total_active_alerts: int
    total_notifications_sent: int
    price_drops_today: int
    alerts_triggered_today: int


# ---- Trending Deals Schemas ----

class TrendingDealOut(BaseModel):
    id: str
    product_id: str
    store: str
    title: str
    brand: Optional[str] = None
    category: str
    image_url: str
    product_url: str
    price: float
    mrp: Optional[float] = None
    discount_percent: float = 0.0
    saved_amount: float = 0.0
    currency: str = "INR"
    availability: str = "in_stock"
    variant: Optional[Dict[str, Any]] = None
    rating: Optional[float] = None
    rating_count: Optional[int] = None
    deal_score: float = 0.0
    historical_badge: Optional[str] = None
    is_live: bool = True
    price_status: str = "verified"
    deal_status: str = "live"
    last_verified_at: str
    freshness: str = "live"
    freshness_label: str = "Price verified recently"

    class Config:
        from_attributes = True


class TrendingDealsResponse(BaseModel):
    updated_at: str
    total_deals: int
    stores_represented: List[str]
    deals: List[TrendingDealOut]


Token.model_rebuild()
ProductDetailOut.model_rebuild()
