from celery import Celery
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

celery_app = Celery(
    'weather_alert',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['celery_tasks']  # ← ЭТО САМОЕ ВАЖНОЕ
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    beat_schedule={
        'check-weather-every-hour': {
            'task': 'celery_tasks.check_all_weather',
            'schedule': 3600.0,
        },
    },
)