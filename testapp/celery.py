import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testapp.settings')

app = Celery('testapp')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()