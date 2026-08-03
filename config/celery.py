import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("drf_project")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.beat_schedule = {
    # Блокировка неактивных пользователей (ежедневно в полночь)
    "block-inactive-users": {
        "task": "users.tasks.block_inactive_users",
        "schedule": crontab(hour=0, minute=0),
        "args": (),
    },
    # Проверка активности каждые 6 часов
    "check-user-activity": {
        "task": "users.tasks.block_inactive_users",
        "schedule": crontab(minute="*/360"),  # Каждые 6 часов
        "args": (),
    },
}
