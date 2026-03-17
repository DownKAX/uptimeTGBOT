import asyncio
from aiogram_dependency import setup_dependency
from aiogram import Bot, Dispatcher

from app.core.settings import settings
from app.telegram_bot.handlers.handler_registration import register_handlers

bot = Bot(settings.TELEGRAM_API)

async def send_newsletter_message(user_id, message, tg_bot=bot):
    await tg_bot.send_message(user_id, message)
    await asyncio.sleep(0.3)

async def main():

    dp = Dispatcher()
    register_handlers(dp)

    setup_dependency(dp)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())