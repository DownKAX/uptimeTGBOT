import os

from celery import Celery
from celery.schedules import crontab

host = os.environ.get('REDIS_HOST', 'localhost')
broker = f'redis://{host}:6379/0'
scheduler = Celery('url_pusher', broker=broker)

scheduler.conf.beat_schedule[f'url_tasks'] = \
    {
        'task': 'celery_tasks.push_url',
        'schedule': crontab(minute='*')
    }
