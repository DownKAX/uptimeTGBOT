from sqlite3 import IntegrityError
from typing import Any, Iterable

import fastapi
from fastapi import HTTPException
from sqlalchemy import select

from app.repositories.models import ColumnValue
from app.utils.UnitOfWork import Uow
from app.api.models.users import Url
from app.database.models import Urls
from app.services.dependencies.validators import unique_validation, exists_validation, exists_validation_none
from dns.asyncresolver import Resolver
from urllib.parse import urlparse
from redis_client import get_async_redis

class UrlService:
    def __init__(self, uow: Uow):
        self.uow = uow

    async def add_one_url(self, data: Url) -> Url:
        r = await get_async_redis()
        data_m = data.model_dump(exclude_none=True)
        async with self.uow:
            result = await unique_validation(self.uow.urls_model.add_one, data_m,
                                       e_message="Some data is not unique, try something else")
            result: Url = Url.model_validate(result.__dict__)
            await self.uow.commit()
        await r.lpush('urls', data.url)
        return result

    async def add_many_urls(self, data: list[Url]) -> list[Url]:
        r = await get_async_redis()
        """Добавляет ссылку в БД. При конфликте(есть такая же запись) увеличивает счётчик, который отражает количество следящих пользователей"""
        data_to_write = [x.model_dump(exclude_none=True) for x in data]

        async with self.uow:
            result: Url = await self.uow.urls_model.add_many(data_to_write,
                                                             conflict={'index_elements': ['url'], 'set_': {'used_by_counter': Urls.used_by_counter + 1}})
            results = [Url.model_validate(x.__dict__) for x in result]

            await self.uow.commit()

        # Добавляем на проверку, чтобы пользователь сразу получил данные
        for x in data:
            await r.lpush('urls', x.url)
        return results

    async def select_one_url(self, return_value: None | str = None, **filters) -> Url | None:
        async with self.uow:
            result = await exists_validation_none(self.uow.urls_model.find_one, e_message="Url does not exist", **filters)
            if result:
                result: Url = Url.model_validate(result.__dict__)
                return result if not return_value else getattr(result, return_value)

    async def select_all_url(self, return_value: str | None = None) -> list[Url] | list[Any]:
        async with self.uow:
            result = await exists_validation(self.uow.urls_model.get_all_data, e_message="db is empty")
            result: list[Url] = [Url.model_validate(r.__dict__) for r in result]
            return result if not return_value else [getattr(x, return_value) for x in result]

    async def delete_data_by_id(self, id: int) -> Url:
        async with self.uow:
            result = await exists_validation(self.uow.urls_model.delete_by_id, id,
                                             e_message="No such example to delete")
            result: Url = Url.model_validate(result.__dict__)
            await self.uow.commit()
            return result

    # colum_and_value - колонка и значение, которые используются для поиска записи в бд, которую будем изменять
    # values - Словарь {"название столбца": новое значение} - станут новыми для записи в бд
    async def update_one_url(self, column_and_value: ColumnValue, values: dict) -> Url:
        async with self.uow:
            result = await unique_validation(self.uow.urls_model.update_one, column_and_value, values,
                                             e_message="Some data is not unique, try something else")
            result: Url = Url.model_validate(result.__dict__)
            await self.uow.commit()
            return result

    async def delete_one_url(self, **data) -> Url:
        async with self.uow:
            result = await exists_validation(self.uow.urls_model.delete_by_data, data)
            result: Url = Url.model_validate(result.__dict__)
            await self.uow.commit()
            return result

    # experiment
    @staticmethod
    async def url_to_ip(url: str) -> str:
        resolver = Resolver()
        u = urlparse(url)
        ip = await resolver.resolve(u.hostname, "A")
        return f'{u.scheme}://{str(ip[0].address)}'