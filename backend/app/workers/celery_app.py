"""Celery entrypoint. Run with:

    celery -A app.workers.celery_app.celery_app worker --loglevel=info
"""
from app.workers.celery_app_ref import celery_app

import app.workers.tasks  # noqa: E402,F401  (register tasks)

__all__ = ["celery_app"]
