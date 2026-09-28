from __future__ import annotations

from typing import Sequence

from pymongo import ASCENDING
from pymongo.asynchronous.database import AsyncDatabase

from uav_assistant.app.interfaces import PathSnapshotRepository
from uav_assistant.domain.models import Path as DomPath
from uav_assistant.infra.db.repos.convertors import PathSnapshotConvertor
from uav_assistant.infra.db.repos.validators import validate_id


class MongoPathSnapshotRepository(PathSnapshotRepository):
    def __init__(
        self,
        database: AsyncDatabase,
        collection_name: str = "path_snapshots",
    ) -> None:
        self._collection = database[collection_name]

    async def create_many(
        self,
        mission_id: int,
        config_id: int,
        paths: Sequence[DomPath],
    ) -> None:
        validate_id(mission_id, "create_many", "Mission")
        validate_id(config_id, "create_many", "AlgorithmConfiguration")
        if not paths:
            return

        documents = [
            PathSnapshotConvertor.to_document(mission_id, config_id, path)
            for path in paths
        ]
        await self._collection.insert_many(documents)

    async def get_all_by_config(self, config_id: int) -> Sequence[DomPath]:
        validate_id(config_id, "get_all_by_config", "AlgorithmConfiguration")
        cursor = (
            self._collection
            .find({"config_id": config_id})
            .sort("generation", ASCENDING)
        )
        documents = await cursor.to_list(length=None)
        return [PathSnapshotConvertor.to_domain(document) for document in documents]

    async def get_by_generation(
        self,
        config_id: int,
        generation: int,
    ) -> DomPath:
        validate_id(config_id, "get_by_generation", "AlgorithmConfiguration")
        document = await self._collection.find_one(
            {
                "config_id": config_id,
                "generation": generation,
            }
        )
        if document is None:
            raise ValueError(
                "[get_by_generation]: "
                f"Path with config_id {config_id} and generation {generation} not found"
            )
        return PathSnapshotConvertor.to_domain(document)

    async def get_minimal_by_config(self, config_id: int) -> DomPath:
        validate_id(config_id, "get_minimal_by_config", "AlgorithmConfiguration")
        document = await self._collection.find_one(
            {"config_id": config_id},
            sort=[("cost", ASCENDING)],
        )
        if document is None:
            raise ValueError(
                f"[get_minimal_by_config]: Path with config_id {config_id} not found"
            )
        return PathSnapshotConvertor.to_domain(document)

    async def delete_by_config(self, config_id: int) -> None:
        validate_id(config_id, "delete_by_config", "AlgorithmConfiguration")
        await self._collection.delete_many({"config_id": config_id})

    async def ensure_indexes(self) -> None:
        await self._collection.create_index(
            [("config_id", ASCENDING), ("generation", ASCENDING)],
            unique=True,
        )
        await self._collection.create_index(
            [("config_id", ASCENDING), ("cost", ASCENDING)],
        )
        await self._collection.create_index("mission_id")
