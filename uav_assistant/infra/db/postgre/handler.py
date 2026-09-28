from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from uav_assistant.settings import POSTGRES_DATABASE


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with POSTGRES_DATABASE.session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
