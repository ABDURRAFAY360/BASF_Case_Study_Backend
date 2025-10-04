from celery import Celery
from app.core.config import settings

celery_app = Celery("bookrec", broker=settings.REDIS_URL, backend=settings.REDIS_URL)
celery_app.conf.timezone = "UTC"
celery_app.conf.beat_schedule = {
    "refresh-books": {"task": "celery_app.tasks.refresh_books", "schedule": 60 * 60 * 6, "args": ()}
}
