import asyncio
import json

from aiogram_dependency import setup_dependency
from aiogram import Bot, Dispatcher

from app.core.settings import settings
from app.telegram_bot.handlers.dependencies import handle_message
from app.telegram_bot.handlers.handler_registration import register_handlers
from redis_client import get_async_redis

bot = Bot(settings.TELEGRAM_API)

async def send_newsletter_message(tg_bot=bot):
    r = await get_async_redis()
    while True:
        # pushing in HttpxClientWorker.py
        message = await r.blpop('tg_messages')
        if message is None:
            continue
        _, message = message
        message = json.loads(message)
        user_id, message = await handle_message(url=message[0], cause=message[1], status=message[2])
        for id in user_id:
            await tg_bot.send_message(id, message, disable_web_page_preview=True)
            await asyncio.sleep(0.3)

async def bot_start():
    dp = Dispatcher()
    register_handlers(dp)

    setup_dependency(dp)

    await dp.start_polling(bot)

async def main():
    await asyncio.gather(send_newsletter_message(), bot_start())

if __name__ == '__main__':
    asyncio.run(main())