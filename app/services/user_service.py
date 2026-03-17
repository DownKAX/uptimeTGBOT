from typing import Any

from fastapi import HTTPException
from sqlalchemy import select

from app.repositories.models import ColumnValue
from app.utils.UnitOfWork import Uow
from app.api.models.users import User
from app.services.dependencies.validators import unique_validation, exists_validation

class UserService:
    def __init__(self, uow: Uow):
        self.uow = uow

    async def add_one_user(self, data: User) -> User:
        data = data.model_dump()
        async with self.uow:
            result = await unique_validation(self.uow.user_model.add_one, data,
                                       e_message="Some data is not unique, try something else")
            result: User = User.model_validate(result.__dict__)
            await self.uow.commit()
            return result

    async def select_one_user(self, return_value: None | str = None, **filters) -> User | None:
        if filters.get('password'):
            raise HTTPException(status_code=401, detail="Forbidden filter")

        async with self.uow:
            result = await exists_validation(self.uow.user_model.find_one, e_message="User does not exist", **filters)
            result: User = User.model_validate(result.__dict__)
            return result if not return_value else [getattr(x, return_value) for x in result]

    async def select_all_users(self, return_value: str | None = None) -> list[User] | list[Any]:
        async with self.uow:
            result = await exists_validation(self.uow.user_model.get_all_data, e_message="db is empty")
            result: list[User] = [User.model_validate(r.__dict__) for r in result]
            return result if not return_value else [getattr(x, return_value) for x in result]

    async def delete_data_by_id(self, id: int) -> User:
        async with self.uow:
            result = await exists_validation(self.uow.user_model.delete_by_id, id,
                                             e_message="No such example to delete")
            result: User = User.model_validate(result.__dict__)
            await self.uow.commit()
            return result

    # colum_and_value - колонка и значение, которые используются для поиска записи в бд, которую будем изменять
    # values - Словарь {"название столбца": новое значение} - станут новыми для записи в бд
    async def update_one_user(self, column_and_value: ColumnValue, values: dict) -> User:
        async with self.uow:
            result = await unique_validation(self.uow.user_model.update_one, column_and_value, values,
                                             e_message="Some data is not unique, try something else")
            result: User = User.model_validate(result.__dict__)
            await self.uow.commit()
            return result