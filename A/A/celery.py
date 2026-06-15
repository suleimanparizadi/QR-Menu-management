# A/celery.py

import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'A.settings')

app = Celery('A')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Help celery to find the task  ********Important********
app.autodiscover_tasks(['accounts'])  

app.conf.beat_schedule = {
    'delete-expired-otp-every-2-minutes': {
        'task': 'accounts.tasks.remove_expired_otps',
        'schedule': crontab(minute='*/2'),
    }
}