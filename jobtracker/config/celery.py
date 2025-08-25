import os
from celery import Celery

# Point Celery to your Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("jobtracker")  # name is arbitrary
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()  # finds tasks.py in installed apps


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
