from aiogram import Dispatcher, F

from app.telegram_bot.handlers.dependencies import RegisteredFilter
from app.telegram_bot.handlers.general_handlers import registration_required
from app.telegram_bot.handlers.url_handlers import add_url_request, add_url, NewUrlState


def register_handlers(dp: Dispatcher):
    F_texts = ['Мониторинг сайта']

    dp.message.register(add_url_request, F.text == 'Мониторинг сайта', RegisteredFilter())
    dp.message.register(add_url, NewUrlState.new_url, RegisteredFilter())

    #access_denied
    dp.message.register(registration_required, F.text.in_(F_texts))