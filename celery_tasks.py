import asyncio

from celery_scheduler import scheduler
from redis_client import get_sync_redis
from app.services.urls_service import UrlService
from app.utils.UnitOfWork import Uow

@scheduler.task()
def push_url():
    r = get_sync_redis()
    uow = Uow()
    url_serv = UrlService(uow)
    urls = asyncio.run(url_serv.select_all_url(return_value='url')) #СОРТИРОВКА
    r.rpush('urls', *urls)
