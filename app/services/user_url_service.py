from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound

from app.api.models.users import UserUrl
from app.services.dependencies.validators import exists_validation, exists_validation_none
from app.utils.UnitOfWork import Uow


class UserUrlService: ## Проверить
    def __init__(self, uow: Uow):
        self.uow = uow

    async def select_one_record(self, **filters) -> UserUrl | None:
        async with self.uow:
            result = await exists_validation_none(self.uow.user_url_model.find_one, **filters)
            if result:
                result: UserUrl = UserUrl.model_validate(result.__dict__)
                return result

    async def add_one_record(self, data: UserUrl):
        data = data.model_dump(exclude_none=True)
        record = await self.select_one_record(**data)
        if record:
            async with self.uow:
                result = await self.uow.user_url_model.add_one(data)
                result: UserUrl = UserUrl.model_validate(result.__dict__)
                await self.uow.commit()
                return result
        else:
            raise HTTPException(status_code=400, detail="You already watching this site")

    async def remove_one_record(self, data: UserUrl):
        data = data.model_dump(exclude_none=True)
        async with self.uow:
            result = await exists_validation(self.uow.user_url_model.remove_one, data, e_message="No such record")
            result: UserUrl = UserUrl.model_validate(result.__dict__)
            await self.uow.commit()
            return result

    async def add_many_records(self, data: list[UserUrl]):
        data_to_write = [x.model_dump(exclude_none=True) for x in data]
        results = []
        async with self.uow:
            result: UserUrl = await self.uow.user_url_model.add_many(data_to_write)
            results.append(result)
            await self.uow.commit()
        return results