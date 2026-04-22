import asyncio
import uvicorn
import multiprocessing
from fastapi import FastAPI

from app.api.endpoints.user_endpoints import user_router
from app.auth.register import auth
from app.middleware.middleware import logging_middleware


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

if __name__ == "__main__":
    multiprocessing.Process(target=main).start()
    multiprocessing.Process(target=email_worker_main).start()
    multiprocessing.Process(target=bot_main).start()
    multiprocessing.Process(target=worker_main())
