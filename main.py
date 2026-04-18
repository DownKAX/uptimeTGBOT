import asyncio
import uvicorn
import multiprocessing
from fastapi import FastAPI

from app.api.endpoints.user_endpoints import user_router
from app.api.models.users import Url
from app.auth.register import auth
from app.middleware.middleware import logging_middleware

from redis_client import get_sync_redis

from app.utils.Email_worker import Email_sender

app = FastAPI()
app.include_router(user_router)
app.include_router(auth)
app.middleware('http')(logging_middleware)


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)

def bot_main():
    from app.telegram_bot.bot import main
    asyncio.run(main())

def email_worker_main():
    email_worker = Email_sender()
    email_worker.worker()

def worker_main():
    from app.utils.HttpxClientWorker import entity
    entity.start_workers()

async def fill_db():
    from app.services.urls_service import UrlService
    from app.utils.UnitOfWork import Uow
    from app.api.models.users import Url

    hosts = {'https://142.251.127.102', 'https://150.171.27.10', 'https://98.137.11.163', 'https://40.114.177.156','https://124.237.177.164', 'https://77.88.55.88', 'https://223.130.200.219', 'https://77.75.77.222','https://77.73.113.1', 'https://188.186.154.79', 'https://188.186.154.79', 'https://162.159.140.229','https://151.101.65.140', 'https://188.186.154.79', 'https://62.115.252.11', 'https://34.149.46.130','https://151.101.128.84', 'https://192.0.77.40', 'https://87.240.132.67', 'https://36.51.224.123','https://162.159.137.232', 'https://149.154.167.99', 'https://3.222.40.237', 'https://142.251.141.78','https://54.74.73.31', 'https://151.101.2.167', 'https://162.159.138.60', 'https://195.8.215.136','https://2.18.64.19', 'https://18.66.102.31', 'https://34.110.155.89', 'https://3.174.46.126','https://98.87.170.71', 'https://2.16.6.12', 'https://47.246.173.237', 'https://47.246.136.156','https://151.101.65.224', 'https://133.237.182.225', 'https://185.73.194.82', 'https://185.62.202.2','https://88.221.168.64', 'https://23.220.112.201', 'https://151.101.194.187', 'https://103.243.32.90','https://3.33.182.45', 'https://140.82.121.4', 'https://172.65.251.78', 'https://185.166.143.49','https://198.252.206.1', 'https://104.16.132.229', 'https://104.19.174.68', 'https://13.32.121.54','https://2.23.90.164', 'https://142.251.141.110', 'https://198.169.1.1', 'https://192.0.66.110','https://151.101.64.223', 'https://151.101.0.223', 'https://104.17.134.117', 'https://188.186.154.79','https://151.101.3.5', 'https://151.101.65.164', 'https://151.101.129.111', 'https://151.101.66.49','https://155.46.172.255', 'https://3.33.146.110', 'https://104.102.37.96', 'https://3.171.214.60','https://83.222.28.15', 'https://81.19.72.32', 'https://151.101.3.1', 'https://52.30.58.64','https://162.159.153.2', 'https://216.119.218.99', 'https://172.64.152.241', 'https://52.69.108.32','https://104.18.32.151', 'https://208.103.161.1', 'https://3.164.230.79', 'https://52.222.149.53','https://162.125.248.18', 'https://142.251.208.174', 'https://142.251.36.110', 'https://52.29.238.212','https://13.227.173.10', 'https://3.33.186.135', 'https://170.114.52.2', 'https://185.15.59.224','https://44.217.252.29', 'https://188.186.154.79', 'https://104.18.37.200', 'https://207.241.224.2','https://17.253.144.10', 'https://13.107.246.53', 'https://211.45.27.231', 'https://13.91.95.74','https://95.100.178.158', 'https://34.194.97.138', 'https://172.64.154.211',
             'https://104.18.32.47'}
    hosts = [Url(url=x) for x in hosts]
    uow = Uow()
    url_serv = UrlService(uow)
    await url_serv.add_many_urls(hosts)

if __name__ == "__main__":
    hosts = [
    "https://google.com",
    "https://youtube.com",
    "https://facebook.com",
    "https://twitter.com",
    "https://instagram.com",
    "https://wikipedia.org",
    "https://amazon.com",
    "https://reddit.com",
    "https://yahoo.com",
    "https://bing.com",
    "https://netflix.com",
    "https://linkedin.com",
    "https://office.com",
    "https://live.com",
    "https://microsoft.com",
    "https://apple.com",
    "https://github.com",
    "https://stackoverflow.com",
    "https://vk.com",
    "https://ok.ru",
    "https://twitch.tv",
    "https://paypal.com",
    "https://imdb.com",
    "https://pinterest.com",
    "https://cnn.com",
    "https://bbc.com",
    "https://nytimes.com",
    "https://forbes.com",
    "https://weather.com",
    "https://dropbox.com",
    "https://cloudflare.com",
    "https://digitalocean.com",
    "https://heroku.com",
    "https://openai.com",
    "https://duckduckgo.com",
    "https://zoom.us",
    "https://slack.com",
    "https://trello.com",
    "https://notion.so",
    "https://figma.com",
    "https://canva.com",
    "https://quora.com",
    "https://medium.com",
    "https://archive.org",
    "https://yandex.ru",
    "https://mail.ru",
    "https://aliexpress.com",
    "https://ebay.com",
    "https://booking.com",
    "https://airbnb.com",
    "https://chotasaie.com"
]
    import json
    hosts = [json.dumps(Url(url=x).__dict__) for x in hosts]
    r = get_sync_redis()
    # for url in hosts:
    #     r.lpush('urls', url)

    multiprocessing.Process(target=main).start()
    multiprocessing.Process(target=email_worker_main).start()
    multiprocessing.Process(target=bot_main).start()
    multiprocessing.Process(target=worker_main())
