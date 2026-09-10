from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from db.database import get_db
from db import models
from core.deps import get_current_admin, get_current_user
from schemas.schemas import AdminStats, UserOut
from typing import List

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/stats", response_model=AdminStats)
def get_admin_stats(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    return {
        "total_users": db.query(func.count(models.User.id)).scalar(),
        "total_products": db.query(func.count(models.Product.id)).scalar(),
        "total_tracked": db.query(func.count(models.UserTrackedProduct.id)).filter(
            models.UserTrackedProduct.tracking_status == models.TrackingStatusEnum.active
        ).scalar(),
        "total_active_alerts": db.query(func.count(models.PriceAlert.id)).filter(
            models.PriceAlert.alert_status == models.AlertStatusEnum.active
        ).scalar(),
        "total_notifications_sent": db.query(func.count(models.Notification.id)).filter(
            models.Notification.status == models.NotificationStatusEnum.sent
        ).scalar(),
        "price_drops_today": db.query(func.count(models.PriceHistory.id)).filter(
            models.PriceHistory.checked_at >= today_start
        ).scalar(),
        "alerts_triggered_today": db.query(func.count(models.PriceAlert.id)).filter(
            models.PriceAlert.last_triggered_at >= today_start
        ).scalar(),
    }


@router.get("/users", response_model=List[UserOut])
def list_users(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    return db.query(models.User).offset(skip).limit(limit).all()


@router.get("/dashboard-stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Get stats for the current user's dashboard."""
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    total_tracked = db.query(func.count(models.UserTrackedProduct.id)).filter(
        models.UserTrackedProduct.user_id == current_user.id,
        models.UserTrackedProduct.tracking_status == models.TrackingStatusEnum.active,
    ).scalar()

    active_alerts = db.query(func.count(models.PriceAlert.id)).filter(
        models.PriceAlert.user_id == current_user.id,
        models.PriceAlert.alert_status == models.AlertStatusEnum.active,
    ).scalar()

    alerts_triggered = db.query(func.count(models.PriceAlert.id)).filter(
        models.PriceAlert.user_id == current_user.id,
        models.PriceAlert.last_triggered_at >= today_start,
    ).scalar()

    products_in_stock = (
        db.query(func.count(models.UserTrackedProduct.id))
        .join(models.Product)
        .filter(
            models.UserTrackedProduct.user_id == current_user.id,
            models.UserTrackedProduct.tracking_status == models.TrackingStatusEnum.active,
            models.Product.availability == models.AvailabilityEnum.in_stock,
        ).scalar()
    )

    products_out_of_stock = (
        db.query(func.count(models.UserTrackedProduct.id))
        .join(models.Product)
        .filter(
            models.UserTrackedProduct.user_id == current_user.id,
            models.UserTrackedProduct.tracking_status == models.TrackingStatusEnum.active,
            models.Product.availability == models.AvailabilityEnum.out_of_stock,
        ).scalar()
    )

    # Price drops today: products where current_price < price 24h ago
    unread_notifications = db.query(func.count(models.Notification.id)).filter(
        models.Notification.user_id == current_user.id,
        models.Notification.read_at == None,
        models.Notification.notification_type == models.NotificationTypeEnum.in_app,
    ).scalar()

    return {
        "total_tracked": total_tracked,
        "active_alerts": active_alerts,
        "alerts_triggered_today": alerts_triggered,
        "products_in_stock": products_in_stock,
        "products_out_of_stock": products_out_of_stock,
        "unread_notifications": unread_notifications,
    }


@router.get("/scraper-health")
def get_scraper_health(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    """
    Returns real-time health metrics of all store scrapers,
    including failing URLs, broken links, recent incidents, and alert channel status.
    """
    from services.admin_alert_service import get_incident_logs
    from core.config import settings

    # Find products with status == 'FAILED' or missing prices
    failing_products = (
        db.query(models.Product)
        .filter(
            (models.Product.status == "FAILED")
            | (models.Product.availability == models.AvailabilityEnum.unavailable)
            | (models.Product.current_price == None)
            | (models.Product.current_price == 0)
        )
        .order_by(models.Product.id.desc())
        .limit(50)
        .all()
    )

    # Store breakdown stats
    store_stats = {}
    for platform_key in ["amazon", "flipkart", "myntra", "ajio", "nykaa"]:
        total_store_prods = db.query(func.count(models.Product.id)).filter(
            models.Product.platform == platform_key
        ).scalar() or 0

        failed_store_prods = db.query(func.count(models.Product.id)).filter(
            models.Product.platform == platform_key,
            (models.Product.status == "FAILED") | (models.Product.current_price == None) | (models.Product.current_price == 0)
        ).scalar() or 0

        success_rate = (
            round(((total_store_prods - failed_store_prods) / total_store_prods) * 100, 1)
            if total_store_prods > 0
            else 100.0
        )

        store_stats[platform_key] = {
            "total": total_store_prods,
            "failed": failed_store_prods,
            "success_rate": success_rate,
            "status": "healthy" if success_rate >= 90 else ("degraded" if success_rate >= 70 else "critical"),
        }

    return {
        "incidents": get_incident_logs(limit=30),
        "failing_products": [
            {
                "id": p.id,
                "product_name": p.product_name,
                "platform": p.platform.value if hasattr(p.platform, "value") else str(p.platform),
                "product_url": p.product_url,
                "current_price": p.current_price,
                "availability": p.availability.value if hasattr(p.availability, "value") else str(p.availability),
                "status": p.status,
                "last_checked": p.last_checked.isoformat() if p.last_checked else None,
                "error_reason": "No price extracted or bot captcha" if not p.current_price else "Page structure changed / unavailable",
            }
            for p in failing_products
        ],
        "store_stats": store_stats,
        "alert_channels": {
            "whatsapp_configured": bool(settings.TWILIO_ACCOUNT_SID and settings.ADMIN_WHATSAPP_NUMBER),
            "whatsapp_recipient": settings.ADMIN_WHATSAPP_NUMBER or "Not Set",
            "telegram_configured": bool(settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_ADMIN_CHAT_ID),
            "telegram_chat_id": settings.TELEGRAM_ADMIN_CHAT_ID or "Not Set",
            "email_configured": bool(settings.SMTP_USER and settings.FIRST_SUPERUSER_EMAIL),
            "email_recipient": settings.FIRST_SUPERUSER_EMAIL or "Not Set",
        },
    }


@router.post("/retry-scrape/{product_id}")
async def retry_product_scrape(
    product_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    """
    Manually triggers an immediate re-scrape for a product to test its URL.
    Updates the product status and clears error if successful.
    """
    from fastapi import HTTPException
    from services.platform_fetcher import async_fetch_product_data
    from services.admin_alert_service import record_incident

    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        data = await async_fetch_product_data(product.product_url)
        if data.success and data.current_price:
            product.current_price = data.current_price
            product.original_price = data.original_price or product.original_price
            product.discount_percentage = data.discount_percentage or product.discount_percentage
            product.availability = data.availability
            product.status = "ACTIVE"
            product.last_checked = datetime.utcnow()
            db.commit()
            return {
                "success": True,
                "message": f"Successfully re-scraped {product.product_name}. New price: ₹{data.current_price}",
                "product": {
                    "id": product.id,
                    "current_price": product.current_price,
                    "status": product.status,
                },
            }
        else:
            error_reason = data.error or "Scraper returned empty price or unverified confidence"
            record_incident(
                store=product.platform.value if hasattr(product.platform, "value") else str(product.platform),
                url=product.product_url,
                error_reason=error_reason,
                product_name=product.product_name,
                severity="ERROR",
            )
            return {
                "success": False,
                "message": f"Scraper retry failed: {error_reason}",
            }
    except Exception as e:
        record_incident(
            store=product.platform.value if hasattr(product.platform, "value") else str(product.platform),
            url=product.product_url,
            error_reason=str(e),
            product_name=product.product_name,
            severity="CRITICAL",
        )
        return {"success": False, "message": f"Exception during retry: {str(e)}"}


@router.post("/test-alert")
async def send_test_admin_alert(
    _: models.User = Depends(get_current_admin),
):
    """
    Sends a test alert across WhatsApp, Telegram, and Email to verify credentials.
    """
    from services.admin_alert_service import send_admin_alert

    res = await send_admin_alert(
        title="Test Alert from Price Ping Admin Console",
        product_name="Sample Product Check (Apple iPhone 15)",
        store="amazon",
        url="https://priceping.store/product/sample-test",
        error_msg="Testing admin alert dispatcher (WhatsApp / Telegram / Email). System operational.",
        failure_count=1,
        force=True,
    )
    return res

