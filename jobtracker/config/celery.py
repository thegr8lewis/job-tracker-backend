import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('jobtracker')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configure Celery Beat Schedule
# app.conf.beat_schedule = {
#     # Daily job fetching at 6 AM
#     'fetch-jobs-daily': {
#         'task': 'applications.tasks.fetch_jobs_daily',
#         'schedule': crontab(hour=6, minute=0),
#         'options': {'queue': 'default'},
#     },
#     # Process emails every hour
#     'process-emails-hourly': {
#         'task': 'applications.tasks.process_all_users_emails',
#         'schedule': crontab(minute=0),
#         'options': {'queue': 'emails'},
#     },
#     # Quick email check every 15 minutes (lightweight)
#     'quick-email-check': {
#         'task': 'applications.tasks.process_all_users_emails',
#         'schedule': crontab(minute='*/15'),
#         'options': {'queue': 'emails', 'expires': 300},  # Expire after 5 minutes
#     },
# }

# Optional: Configure task routes for better queue management
app.conf.task_routes = {
    'applications.tasks.fetch_jobs_daily': {'queue': 'default'},
    'applications.tasks.process_user_emails': {'queue': 'emails'},
    'applications.tasks.process_all_users_emails': {'queue': 'emails'},
}

# Optional: Configure task time limits
app.conf.task_time_limit = 300  # 5 minutes max per task
app.conf.task_soft_time_limit = 240  # 4 minutes soft limit

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


if os.name == 'nt':  # Windows
    # Use solo pool for Windows to avoid process issues
    app.conf.worker_pool = 'solo'
    # Or use threads pool for better performance
    # app.conf.worker_pool = 'threads'
    app.conf.worker_concurrency = 4  # Reduce concurrency on Windows