from abc import ABC, abstractmethod

from app.database.db import get_session_maker

# Строка с импортом ниже служит примером. Там следует хранить свои репозитории
from app.repositories.project_repository import UserRepository, UrlsRepository


class AbstractUow(ABC):
    model: None

    @abstractmethod
    def __init__(self):
        ...

    @abstractmethod
    async def __aenter__(self, exc_type, exc_val, exc_tb):
        ...

    @abstractmethod
    async def __aexit__(self):
        ...

    @abstractmethod
    async def commit(self):
        ...

    @abstractmethod
    async def rollback(self):
        ...

class Uow(AbstractUow):
    def __init__(self):
        self.session_maker = get_session_maker()

    async def __aenter__(self):
        self.session = self.session_maker()
        # Все репозитории должны быть в одном UnitOfWork и определены в этом методе следующим образом:
        self.user_model = UserRepository(self.session)
        self.urls_model = UrlsRepository(self.session)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.commit()
        await self.session.rollback()
        await self.session.close()

        self.session = None

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
