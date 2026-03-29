from ftplib import all_errors

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.api.models.users import Url, UserUrl, JoinedUserUrl
from app.repositories.models import ColumnValue
from app.telegram_bot.handlers.dependencies import url_dependency, user_url_dependency, user_dependency, check_url, \
    check_access_to_url
from app.telegram_bot.keyboards.common_keyboards import back_button_markup, build_inline_keyboard, \
 build_user_url_interactions_markup


class NewUrlState(StatesGroup):
    new_url = State()

async def add_url_request(message: types.Message, state: FSMContext):
    await message.answer(text='Следующим сообщением напишите ссылку(или несколько, каждая на новой строке) на желаемый сайт в формате:\nhttps://mysite.com\nhttp://mysite.com', disable_web_page_preview=True, reply_markup=back_button_markup)
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

    await message.answer(text=answer_to_user, disable_web_page_preview=True, reply_markup=back_button_markup)

async def remove_url(callback_data: types.CallbackQuery, url_service: url_dependency, user_url_service: user_url_dependency):
    _, user_id, url_id = callback_data.data.split('_')
    user_id, url_id = int(user_id), int(url_id)
    record = await check_access_to_url(callback_data, url_id)
    if record is None:
        await callback_data.message.answer('Нет доступа')
        await callback_data.answer()
    else:
        monitoring_users_count = await url_service.select_one_url(return_value='used_by_counter', id=url_id)
        if monitoring_users_count != 1:
            await url_service.update_one_url(column_and_value=ColumnValue(column_name='id', column_value=url_id), values={'used_by_counter': monitoring_users_count - 1})
            await user_url_service.remove_one_record(UserUrl(user_id=user_id, url_id=url_id))
        else:
            await url_service.delete_one_url(id=url_id)
        await callback_data.message.answer('Успешно удалено')
        await callback_data.answer()


async def show_user_his_urls(message: types.Message, user_service: user_dependency, user_url_service: user_url_dependency):
    user_id = await user_service.select_one_user(return_value='id', telegram_id=message.from_user.id)
    user_urls: list[int] | None = await user_url_service.select_all_records(return_value='url_id', user_id=user_id)
    url_names: list[JoinedUserUrl] = await user_url_service.join_with_url(clause_self_model='url_id', clause_url_model='id', user_id=user_id)
    markup = await build_inline_keyboard(url_names)

    if user_urls:
        await message.answer('Ваши ресурсы:', reply_markup=markup)
    else:
        await message.answer('Вы пока что не следите за сайтами')

async def show_url_data(callback: types.CallbackQuery, url_service: url_dependency, user_service: user_dependency):
    _, url_id = callback.data.split('_')
    url_id = int(url_id)
    url_name: str = await url_service.select_one_url(return_value='url', id=url_id)
    user_id = await user_service.select_one_user(return_value='id', telegram_id=callback.from_user.id)

    record = await check_access_to_url(callback, url_id)

    if record is None:
        await callback.message.answer('Нет доступа')
        await callback.answer()
    else:
        interactions_markup = await build_user_url_interactions_markup(user_id=user_id, url_id=url_id)
        await callback.message.answer(text=f'Ваш ресурс:\n{url_name}', reply_markup=interactions_markup, disable_web_page_preview=True)
        await callback.answer()