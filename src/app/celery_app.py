from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "basf_bookrec",
    broker=settings.REDIS_URL,
    backend=settings.CELERY_RESULT_BACKEND or settings.REDIS_URL,
    include=["app.task.books"],  # auto-discover tasks in the specified module
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
)

# Periodic schedule (Celery Beat) — refresh every 12 hours
celery_app.conf.beat_schedule = {
    "refresh-books-every-12h": {
        "task": "app.task.books.refresh_books",
        "schedule": 60 * 60 * 12,  # every 12 hours
        "args": ["Harry Potter", 10],  # default params: query, limit
    }
}
