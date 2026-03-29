from aiogram import Dispatcher, F
from aiogram.filters import Command

from app.telegram_bot.handlers.dependencies import RegisteredFilter
from app.telegram_bot.handlers.general_handlers import registration_required, start_handler, back_handler
from app.telegram_bot.handlers.url_handlers import add_url_request, add_url, NewUrlState, show_user_his_urls, \
    show_url_data, remove_url


def register_handlers(dp: Dispatcher):
    F_texts = ['Мониторинг сайта', 'Мои ресурсы']
    F_datas = ['back']

    # commands
    dp.message.register(start_handler, Command(commands=['start']), RegisteredFilter())

    # general
    dp.callback_query.register(back_handler, F.data == 'back', RegisteredFilter())

    # url
    dp.message.register(show_user_his_urls, F.text == 'Мои ресурсы', RegisteredFilter())
    dp.message.register(add_url_request, F.text == 'Мониторинг сайта', RegisteredFilter())
    dp.message.register(add_url, NewUrlState.new_url, RegisteredFilter())
    dp.callback_query.register(show_url_data, F.data.startswith('urlrequest_'), RegisteredFilter())
    dp.callback_query.register(remove_url, F.data.startswith('delrequest_'), RegisteredFilter())

    #access_denied
    dp.message.register(registration_required, F.text.in_(F_texts))
    dp.message.register(registration_required, F.data.in_(F_datas))
    dp.message.register(registration_required, Command(commands=['start']))
    dp.callback_query.register(registration_required, F.data.startswith('urlrequest_'))
    dp.callback_query.register(registration_required, F.data.startswith('delrequest_'))
