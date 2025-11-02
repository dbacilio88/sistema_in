"""
Celery configuration for Traffic Infraction Detection System.
"""
import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('traffic_admin')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule for periodic tasks
app.conf.beat_schedule = {
    'sync-sunarp-data': {
        'task': 'vehicles.tasks.sync_sunarp_data',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'cleanup-old-videos': {
        'task': 'infractions.tasks.cleanup_old_videos',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM
    },
    'generate-daily-report': {
        'task': 'infractions.tasks.generate_daily_report',
        'schedule': crontab(hour=23, minute=30),  # Daily at 11:30 PM
    },
    'check-device-health': {
        'task': 'devices.tasks.check_device_health',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery setup"""
    print(f'Request: {self.request!r}')
