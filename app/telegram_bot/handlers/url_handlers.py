from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from urllib.parse import urlparse

from app.api.models.users import Url, UserUrl
from app.telegram_bot.handlers.dependencies import url_dependency, user_url_dependency, user_dependency, check_url

class NewUrlState(StatesGroup):
    new_url = State()

async def add_url_request(message: types.Message, state: FSMContext):
    await message.answer(text='Следующим сообщением напишите ссылку(или несколько, каждая на новой строке) на желаемый сайт в формате:\nhttps://mysite.com\nhttp://mysite.com', disable_web_page_preview=True)
    await state.set_state(NewUrlState.new_url)

async def add_url(message: types.Message, state: FSMContext, user_service: user_dependency, url_service: url_dependency, user_url_service: user_url_dependency):
    answer_to_user = ''
    urls = {'to_write_urls': [], 'wrong_format': [], 'repeated': []}
    # id для добавления в таблицу: id пользователя - id отслеживаемого сайта; и проверок
    user_id = await user_service.select_one_user(return_value='id', telegram_id=message.from_user.id)
    urls_from_user = message.text.split('\n') # Список ссылок, полученных от пользователя

    for url in urls_from_user:
        check_result = await check_url(url, user_id)
        if isinstance(check_result, int | None):
            urls['to_write_urls'].append(Url(url=url))
        else:
            urls[check_result].append(url)


    if urls['to_write_urls']: # если есть что записывать
        ids = await url_service.add_many_urls(urls['to_write_urls'])
        ids = [x.id for x in ids]
        await user_url_service.add_many_records([UserUrl(user_id=user_id, url_id=x) for x in ids])
        await state.clear()
        await state.set_state(None)
        answer_to_user += 'Успешно добавлены ссылки\n'
        for x in urls['to_write_urls']:
            answer_to_user += f'{x.url}\n'

    if urls['repeated']:
        answer_to_user += '\nСледующие ссылки уже в мониторинге и не добавились\n'
        for x in urls['repeated']:
            answer_to_user += f'{x}\n'

    if urls['wrong_format']:
        answer_to_user += '\nСледующие ссылки неверны, попробуй снова\n'
        for x in urls['wrong_format']:
            answer_to_user += f'{x}\n'

    await message.answer(text=answer_to_user, disable_web_page_preview=True)