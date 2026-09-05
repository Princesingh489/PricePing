from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Enum, ForeignKey, Text, Index
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from db.database import Base


class PlatformEnum(str, enum.Enum):
    amazon = "amazon"
    flipkart = "flipkart"
    ajio = "ajio"
    myntra = "myntra"
    nykaa = "nykaa"
    unknown = "unknown"


class AvailabilityEnum(str, enum.Enum):
    in_stock = "in_stock"
    low_stock = "low_stock"
    out_of_stock = "out_of_stock"
    unavailable = "unavailable"
    unknown = "unknown"


class TrackingStatusEnum(str, enum.Enum):
    active = "active"
    paused = "paused"
    deleted = "deleted"


class AlertTypeEnum(str, enum.Enum):
    below_price = "below_price"
    price_range = "price_range"
    percentage_drop = "percentage_drop"


class AlertStatusEnum(str, enum.Enum):
    active = "active"
    triggered = "triggered"
    snoozed = "snoozed"
    disabled = "disabled"


class NotificationTypeEnum(str, enum.Enum):
    email = "email"
    push = "push"
    sms = "sms"
    in_app = "in_app"
    call = "call"


class NotificationStatusEnum(str, enum.Enum):
    pending = "pending"
    sent = "sent"
    failed = "failed"
    read = "read"


# ------- MODELS -------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tracked_products = relationship("UserTrackedProduct", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("PriceAlert", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(Enum(PlatformEnum), nullable=False)
    store = Column(String(50), nullable=True, index=True)  # Store identifier: amazon, flipkart, etc.
    external_product_id = Column(String(100), nullable=True, index=True)  # ASIN, SKU, PID
    product_name = Column(String(500), nullable=False)
    product_url = Column(Text, nullable=False)
    product_image = Column(Text, nullable=True)
    images_json = Column(Text, nullable=True)  # JSON-encoded list of image URLs for gallery
    colors_json = Column(Text, nullable=True)  # JSON-encoded list of color swatches
    brand = Column(String(150), nullable=True)
    model = Column(String(150), nullable=True)
    variant = Column(String(250), nullable=True)  # Storage, color, RAM, size
    variants_json = Column(Text, nullable=True)   # JSON array of {size, price, mrp, in_stock}
    current_price = Column(Float, nullable=True)
    original_price = Column(Float, nullable=True)
    discount_percentage = Column(Float, nullable=True)
    lowest_price = Column(Float, nullable=True)
    highest_price = Column(Float, nullable=True)
    average_price = Column(Float, nullable=True)
    history_state = Column(String(50), default="ORGANIC_COLD_START", index=True)  # 'AGGREGATED_2YR', 'ORGANIC_COLD_START'
    canonical_id = Column(String(100), nullable=True, index=True)
    canonical_url = Column(Text, nullable=True)
    title = Column(String(500), nullable=True)
    image_url = Column(Text, nullable=True)
    rating = Column(Float, nullable=True)
    rating_count = Column(Integer, nullable=True)
    review_count = Column(Integer, nullable=True)
    currency = Column(String(10), default="INR")
    availability = Column(Enum(AvailabilityEnum), default=AvailabilityEnum.unknown)
    status = Column(String(50), default="PENDING", index=True)  # 'PENDING', 'ACTIVE', 'FAILED'
    description = Column(Text, nullable=True)
    observed_at = Column(DateTime, nullable=True)
    last_checked = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_products_store_external_id", "store", "external_product_id"),
    )

    price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")
    tracked_by = relationship("UserTrackedProduct", back_populates="product", cascade="all, delete-orphan")
    alerts = relationship("PriceAlert", back_populates="product", cascade="all, delete-orphan")
    offers = relationship("ProductOffer", back_populates="product", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="product", cascade="all, delete-orphan")

    @property
    def colors(self):
        if self.colors_json:
            try:
                import json
                data = json.loads(self.colors_json)
                if isinstance(data, list):
                    return data
            except Exception:
                pass
        return []

    @property
    def variants(self):
        if self.variants_json:
            try:
                import json
                data = json.loads(self.variants_json)
                if isinstance(data, list):
                    return data
            except Exception:
                pass
        return []

    @property
    def images(self):
        if self.images_json:
            try:
                import json
                data = json.loads(self.images_json)
                if isinstance(data, list) and len(data) > 0:
                    return data
            except Exception:
                pass
        if self.product_image:
            return [self.product_image]
        return []


class ProductOffer(Base):
    """
    Live/cached cross-store product offers for comparison across supported stores.
    """
    __tablename__ = "product_offers"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    store = Column(String(50), nullable=False, index=True)  # amazon, flipkart, myntra, ajio, nykaa
    external_product_id = Column(String(100), nullable=True, index=True)
    seller_name = Column(String(200), nullable=True)
    seller_id = Column(String(100), nullable=True)
    price = Column(Float, nullable=True)
    original_price = Column(Float, nullable=True)
    shipping_price = Column(Float, default=0.0)
    delivery_text = Column(String(150), nullable=True)
    coupon_text = Column(String(150), nullable=True)
    availability = Column(Enum(AvailabilityEnum), default=AvailabilityEnum.unknown)
    url = Column(Text, nullable=True)
    is_verified_match = Column(Boolean, default=True)
    match_confidence = Column(Float, nullable=True)
    match_signals_json = Column(Text, nullable=True)
    match_reason = Column(String(250), nullable=True)
    variants_json = Column(Text, nullable=True)  # JSON array of per-size variants
    observed_at = Column(DateTime, default=datetime.utcnow)
    last_checked_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="offers")

    __table_args__ = (
        Index("ix_product_offers_product_store", "product_id", "store"),
    )


class UserTrackedProduct(Base):
    __tablename__ = "user_tracked_products"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    tracking_status = Column(Enum(TrackingStatusEnum), default=TrackingStatusEnum.active)
    target_min_price = Column(Float, nullable=True)
    target_max_price = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="tracked_products")
    product = relationship("Product", back_populates="tracked_by")


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    store = Column(String(50), nullable=True, index=True)  # e.g. amazon, flipkart, myntra
    external_product_id = Column(String(100), nullable=True, index=True)
    price = Column(Float, nullable=False)
    original_price = Column(Float, nullable=True)
    currency = Column(String(10), default="INR")
    availability = Column(Enum(AvailabilityEnum), default=AvailabilityEnum.unknown)
    seller = Column(String(200), nullable=True)
    source = Column(String(50), default="priceping_observation")  # priceping_observation, keepa, etc.
    verified = Column(Boolean, default=True)
    is_backfilled = Column(Boolean, default=False, index=True)
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)
    checked_at = Column(DateTime, default=datetime.utcnow, index=True)

    product = relationship("Product", back_populates="price_history")

    __table_args__ = (
        Index("ix_price_history_product_store", "product_id", "store"),
        Index("ix_price_history_product_recorded", "product_id", "recorded_at", unique=True),
    )


# Multi-user mapping alias for tracking subscriptions
UserProductSubscription = UserTrackedProduct


class PriceProvider(Base):
    """
    Configuration and registry for historical price providers (e.g. Keepa, PricePing observations).
    """
    __tablename__ = "price_providers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    store = Column(String(50), nullable=False, index=True)  # amazon, flipkart, all
    provider_type = Column(String(50), nullable=False)      # keepa, priceping_observation, official_api
    enabled = Column(Boolean, default=True)
    configuration = Column(Text, nullable=True)            # JSON config
    created_at = Column(DateTime, default=datetime.utcnow)


class PriceAlert(Base):
    __tablename__ = "price_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    alert_type = Column(Enum(AlertTypeEnum), nullable=False)
    target_price = Column(Float, nullable=True)          # For below_price type
    minimum_price = Column(Float, nullable=True)          # For price_range type
    maximum_price = Column(Float, nullable=True)          # For price_range type
    percentage_drop = Column(Float, nullable=True)        # For percentage_drop type
    base_price = Column(Float, nullable=True)             # Price when alert was set
    alert_status = Column(Enum(AlertStatusEnum), default=AlertStatusEnum.active)
    last_triggered_at = Column(DateTime, nullable=True)
    last_triggered_price = Column(Float, nullable=True)
    is_in_range = Column(Boolean, default=False)          # Tracks if condition is currently met
    notify_email = Column(Boolean, default=True)
    notify_push = Column(Boolean, default=True)
    notify_sms = Column(Boolean, default=False)
    notify_in_app = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="alerts")
    product = relationship("Product", back_populates="alerts")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    notification_type = Column(Enum(NotificationTypeEnum), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(Enum(NotificationStatusEnum), default=NotificationStatusEnum.pending)
    sent_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")
    product = relationship("Product", back_populates="notifications")


class Deal(Base):
    """
    Live Verified Deals across Amazon, Flipkart, Myntra, AJIO, and Nykaa.
    Maintained by DealEngine with strict real-time validation and automatic replacement.
    """
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    deal_key = Column(String(150), unique=True, index=True, nullable=False)
    canonical_product_id = Column(String(100), nullable=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True, index=True)
    store = Column(String(50), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    brand = Column(String(150), nullable=True)
    category = Column(String(100), default="General", index=True)
    product_url = Column(Text, nullable=False)
    image_url = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    mrp = Column(Float, nullable=True)
    discount_percent = Column(Float, nullable=True)
    currency = Column(String(10), default="INR")
    availability = Column(String(50), default="in_stock")
    variant_info = Column(Text, nullable=True)
    rating = Column(Float, default=4.2)
    rating_count = Column(Integer, default=1000)
    deal_score = Column(Float, default=50.0, index=True)
    historical_badge = Column(String(100), nullable=True)
    deal_status = Column(String(50), default="LIVE", index=True)
    price_status = Column(String(50), default="verified")
    is_live = Column(Boolean, default=True, index=True)
    last_verified_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
