from aiogram.types import (KeyboardButton as KB, ReplyKeyboardMarkup as RKM,
                           InlineKeyboardMarkup as IKM, InlineKeyboardButton as IKB)

from app.api.models.users import JoinedUserUrl

crud_sites = [[KB(text='Мониторинг сайта'), KB(text='Мои ресурсы')]]
сrud_markup = RKM(keyboard=crud_sites, resize_keyboard=True)

back_button = [[IKB(text='Назад', callback_data='back')]]
back_button_markup = IKM(inline_keyboard=back_button)

async def build_user_url_interactions_markup(user_id: int, url_id: int):
    user_url_interactions = [[IKB(text='Удалить', callback_data=f'delrequest_{user_id}_{url_id}')]]
    user_url_interactions_markup = IKM(inline_keyboard=user_url_interactions)
    return user_url_interactions_markup

async def build_inline_keyboard(urls: list[JoinedUserUrl]):
    urls_buttons = [IKB(text=x.url, callback_data=f'urlrequest_{str(x.url_id)}') for x in urls]
    urls_buttons = [urls_buttons[x-2:x] for x in range(2, len(urls_buttons) + 2, 2)]
    return IKM(inline_keyboard=urls_buttons)