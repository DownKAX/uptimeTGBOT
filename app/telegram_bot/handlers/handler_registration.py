from aiogram import Dispatcher, F
from app.telegram_bot.handlers.url_handlers import add_url_request, add_url, NewUrlState


def register_handlers(dp: Dispatcher):
    dp.message.register(add_url_request, F.text == 'Мониторинг сайта')
    dp.message.register(add_url, NewUrlState.new_url)