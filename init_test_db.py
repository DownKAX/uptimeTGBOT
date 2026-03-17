import asyncio
import asyncpg
from app.core.settings import settings

POSTGRES_DSN = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.POSTGRES_DB}"   # системная БД


async def create_test_db():
    conn = await asyncpg.connect(POSTGRES_DSN)
    exists = await conn.fetchval(
        "SELECT 1 FROM pg_database WHERE datname = $1",
        settings.POSTGRES_DB_TEST,
    )

    if not exists:
        await conn.execute(f'CREATE DATABASE "{settings.POSTGRES_DB_TEST}"')
        print("Test database created")
    else:
        print("Test database already exists")

    await conn.close()

if __name__ == "__main__":
    asyncio.run(create_test_db())