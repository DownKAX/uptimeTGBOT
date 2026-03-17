from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from urllib.parse import urlparse

from app.api.models.users import Url
from app.telegram_bot.handlers.dependencies import url_dependency

class NewUrlState(StatesGroup):
    new_url = State()

async def add_url_request(message: types.Message, state: FSMContext):
    await message.answer(text='Следующим сообщением напишите ссылку(или несколько, каждая на новой строке) на желаемый сайт в формате:\nhttps://mysite.com\nhttp://mysite.com', disable_web_page_preview=True)
    await state.set_state(NewUrlState.new_url)

async def add_url(message: types.Message, state: FSMContext, url_service: url_dependency):
    urls_to_write = []
    urls_from_user = message.text.split('\n') # Добавлять несколько
    print(urls_from_user)
    for url in urls_from_user:
        url_parsed = urlparse(url)
        if url_parsed.scheme and url_parsed.netloc and not(" " in url):
            urls_to_write.append(Url(url=url))
        else:
            await message.answer(f'Формат введённой ссылки неверен:\n{url}\nВведите всё заново')
            urls_to_write.clear()
            break
    else:
        await url_service.add_many_urls(urls_to_write)
        await message.answer('Успешно добавлено')
        await state.clear()
        await state.set_state(None)


