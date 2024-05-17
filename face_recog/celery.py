# celery.py

from __future__ import absolute_import, unicode_literals
from . import settings
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'face_recog.settings')

app = Celery('face_recog', broker='redis://redis:6379/0')

# app.conf.broker_url('redis://localhost:6379/0')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

