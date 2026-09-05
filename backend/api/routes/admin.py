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
