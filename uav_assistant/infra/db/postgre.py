from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import uav_assistant.infra.db.url_builder as url_builder
from dotenv import load_dotenv
import os

env_file = os.path.join(os.path.dirname(__file__), '../../../.env')
load_dotenv(dotenv_path=env_file)

url = url_builder.build(
    "PGASYNCDRIVER",
    "PGROLE",
    "PGPASSWORD",
    "PGHOST",
    "PGPORT",
    "PGDATABASE"
)
Session = async_sessionmaker(create_async_engine(url), class_=AsyncSession, expire_on_commit=False)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with Session() as session:
        try:
            yield session
            await session.commit()
        finally:
            await session.rollback()

