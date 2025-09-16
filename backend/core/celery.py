import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.core.settings")

app = Celery("dev_mentor")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
