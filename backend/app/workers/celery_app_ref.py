"""Single Celery instance, imported by both the app factory and the tasks
module to avoid a circular import."""
from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "studio",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    broker_connection_retry_on_startup=True,
)

task = celery_app.task
