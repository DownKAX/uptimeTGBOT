from fastapi.exceptions import HTTPException

from aiogram.filters import BaseFilter
from typing import Annotated

from aiogram.types import TelegramObject
from aiogram_dependency import Depends, Scope

from app.services.user_service import UserService
from app.services.urls_service import UrlService
from app.utils.UnitOfWork import Uow, AbstractUow

async def get_url_service(uow: AbstractUow = Uow()):
    return UrlService(uow)

async def get_user_service(uow: AbstractUow = Uow()):
    return UserService(uow)

url_dependency = Annotated[UrlService, Depends(get_url_service, scope=Scope.TRANSIENT)]
user_dependency = Annotated[UserService, Depends(get_user_service, scope=Scope.TRANSIENT)]

class RegisteredFilter(BaseFilter):
    async def __call__(self, obj: TelegramObject) -> bool:
        user_service = await get_user_service()
        try:
            db_user_id = await user_service.select_one_user(filters={'telegram_id': obj.from_user.id})
        except HTTPException:
            return None
        return bool(db_user_id)