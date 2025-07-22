from sqlalchemy.ext.asyncio import AsyncSession
from src.database.engine import db


async def get_session() -> AsyncSession:
    async with db.get_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
