import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GymGeniusAI.settings')

app = Celery('GymGeniusAI')

# Load config from Django settings, using a CELERY_ prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all apps
app.autodiscover_tasks()
