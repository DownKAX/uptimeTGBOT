from fastapi import Depends
from typing import Annotated

from app.utils.UnitOfWork import Uow, AbstractUow
from app.services.user_service import UserService

async def get_user_service(uow: AbstractUow = Depends(Uow)):
    return UserService(uow)

user_dependency = Annotated[UserService, Depends(get_user_service)]