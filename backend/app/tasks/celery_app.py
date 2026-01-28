"""Celery application configuration."""

from celery import Celery
from app.config import settings

celery_app = Celery(
    "fms",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.alerts"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)

# Celery Beat schedule
celery_app.conf.beat_schedule = {
    "check-low-stock-alerts": {
        "task": "app.tasks.alerts.check_low_stock_alerts_task",
        "schedule": 3600.0,  # Every hour
    },
    "calculate-daily-storage-charges": {
        "task": "app.tasks.alerts.calculate_daily_storage_charges",
        "schedule": 86400.0,  # Daily at midnight
    },
}
