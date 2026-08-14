from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
# from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scattering.settings')

app = Celery('scattering_celery')

# 使用Django的settings配置
app.config_from_object('django.conf:settings', namespace='CELERY')
# app.conf.broker_url = settings.CELERY_BROKER_URL
# app.conf.result_backend = settings.CELERY_RESULT_BACKEND

# 自动发现任务
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
