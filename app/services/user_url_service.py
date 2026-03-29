from fastapi import HTTPException

from app.api.models.users import UserUrl, JoinedUserUrl
from app.database.models import Urls
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

    async def select_all_records(self, return_value: str | None = None, **filters):
        async with self.uow:
            result = await exists_validation_none(self.uow.user_url_model.find_several, **filters)
            if result:
                result: list[UserUrl] = [UserUrl.model_validate(x.__dict__) for x in result]
                return [getattr(x, return_value) for x in result] if return_value else result

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
            result = await exists_validation(self.uow.user_url_model.delete_by_data, data, e_message="No such record")
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

    async def join_with_url(self, clause_self_model: str, clause_url_model: str, **filters) -> list[JoinedUserUrl]:
        async with self.uow:
            result: list[tuple[int, int, str]] = await self.uow.user_url_model.join(Urls, clause_self_model, clause_url_model, [(0, 'user_id'), (0, 'url_id'), (1, 'url')], **filters)
            result: list[JoinedUserUrl] = [JoinedUserUrl(user_id=x[0], url_id=x[1], url=x[2]) for x in result]
            return result
