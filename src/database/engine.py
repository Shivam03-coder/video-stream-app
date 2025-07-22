# src/core/database.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from src.configs.env_config import env

Base = declarative_base()


class Database:
    print(env.DATABASE_URL)

    def __init__(self):
        self._engine = create_async_engine(env.DATABASE_URL, echo=True, future=True)
        self._SessionLocal = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

    def get_session(self) -> AsyncSession:
        return self._SessionLocal()

    async def init(self):
        import src.database.models

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self):
        await self._engine.dispose()


db = Database()
