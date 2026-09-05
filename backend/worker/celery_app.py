"""
Celery Application Configuration
"""
from celery import Celery
from core.config import settings

celery_app = Celery(
    "pricewatch",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        "check-all-product-prices": {
            "task": "worker.tasks.check_all_prices",
            "schedule": float(settings.PRICE_CHECK_INTERVAL_HOURS * 3600),  # Configurable e.g. every 6 hours
        },
        "refresh-trending-deals": {
            "task": "worker.tasks.refresh_trending_deals_task",
            "schedule": 300.0,  # Every 5 minutes
        },
    },
)
