from urllib.parse import urlparse
from sqlalchemy import text

from fastapi.exceptions import HTTPException

from aiogram.filters import BaseFilter
from typing import Annotated

from aiogram.types import TelegramObject
from aiogram_dependency import Depends, Scope

from app.api.models.users import UserUrl
from app.services.user_service import UserService
from app.services.urls_service import UrlService
from app.services.user_url_service import UserUrlService
from app.utils.UnitOfWork import Uow, AbstractUow
from app.database.db import get_session

async def get_url_service(uow: AbstractUow = Uow()):
    return UrlService(uow)

async def get_user_service(uow: AbstractUow = Uow()):
    return UserService(uow)

async def get_user_url_service(uow: AbstractUow = Uow()):
    return UserUrlService(uow)

url_dependency = Annotated[UrlService, Depends(get_url_service, scope=Scope.TRANSIENT)]
user_dependency = Annotated[UserService, Depends(get_user_service, scope=Scope.TRANSIENT)]
user_url_dependency = Annotated[UserUrlService, Depends(get_user_url_service, scope=Scope.TRANSIENT)]

class RegisteredFilter(BaseFilter):
    async def __call__(self, obj: TelegramObject) -> bool:
        user_service = await get_user_service()
        try:
            db_user_id = await user_service.select_one_user(telegram_id=obj.from_user.id)
        except HTTPException:
            return None
        return bool(db_user_id)

async def check_url(url, user_id: int) -> str | int | None:
    """ Проверяет ссылку на то что её формат верен и используется ли она уже пользователем для мониторинга"""
    url_parsed = urlparse(url)

    # Проверка корректности ссылки
    if not (url_parsed.scheme and url_parsed.netloc and not (" " in url)):
        return 'wrong_format'

    # Проверка повторения
    uow = Uow()
    url_service = await get_url_service(uow)
    user_url_service = await get_user_url_service(uow)
    url_id: int | None = await url_service.select_one_url(url=url, return_value='id')
    if not (url_id is None or \
            (is_repeated := await user_url_service.select_one_record(user_id=user_id, url_id=url_id)) is None):
        return 'repeated'

    return url_id

async def check_access_to_url(callback, url_id) -> UserUrl | None:
    user_url_service = await get_user_url_service()
    user_service = await get_user_service()

    user_id = await user_service.select_one_user(return_value='id', telegram_id=callback.from_user.id)
    record = await user_url_service.select_one_record(user_id=user_id, url_id=url_id)
    return record

async def handle_message(url: str, cause: str, status: str) -> (list[int], str):
    """Строит сообщение для рассылки, которая происходит после падения или оживления сайта.
    Вызывает соответсвующую функцию, которая создает инциденты или завершает их"""
    url_service = await get_url_service()
    user_url_service = await get_user_url_service()
    message = f'{url} {'недоступен' if status == "DOWN" else 'снова доступен'}{f"\nПричина {cause}" if cause else ""}'
    url_id = await url_service.select_one_url(return_value='id', url=url)
    user_ids = await user_url_service.select_all_records(return_value='user_id', url_id=url_id)

    async for session in get_session():
        result = await session.execute(text("""SELECT telegram_id FROM users WHERE id = ANY(:ids)"""), {"ids": user_ids})
        user_tg_ids = result.scalars().all()

    if status == "DOWN":
        await start_incident(url)
    else:
        await end_incident(url)

    return user_tg_ids, message

async def start_incident(url: str):
    pass

async def end_incident(url: str):
    pass