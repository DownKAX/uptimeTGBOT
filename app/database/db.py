from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.settings import settings

BASE_URL = settings.DATABASE_URL

def get_session_maker():
    engine = create_async_engine(url=BASE_URL)
    return async_sessionmaker(autocommit=False, expire_on_commit=False, bind=engine, class_=AsyncSession)

async def get_session():
    engine = create_async_engine(url=BASE_URL)
    AsyncMaker = async_sessionmaker(autocommit=False, expire_on_commit=False, bind=engine, class_=AsyncSession)
    async with AsyncMaker() as session:
        yield session

