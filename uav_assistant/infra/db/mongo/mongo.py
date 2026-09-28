from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from uav_assistant.infra.db.urls import get_mongodb_database, get_mongodb_uri
from uav_assistant.infra.db.repos.path import MongoPathSnapshotRepository


class MongoDatabase:
    def __init__(self) -> None:
        self._client: AsyncMongoClient | None = None
        self._database: AsyncDatabase | None = None

    async def connect(self) -> None:
        if self._client is not None:
            return

        self._client = AsyncMongoClient(get_mongodb_uri())
        self._database = self._client[get_mongodb_database()]
        try:
            await MongoPathSnapshotRepository(self.database).ensure_indexes()
        except Exception:
            await self.close()
            raise

    async def close(self) -> None:
        if self._client is not None:
            await self._client.close()
        self._client = None
        self._database = None

    @property
    def database(self) -> AsyncDatabase:
        if self._database is None:
            raise RuntimeError("MongoDB is not initialized")
        return self._database



