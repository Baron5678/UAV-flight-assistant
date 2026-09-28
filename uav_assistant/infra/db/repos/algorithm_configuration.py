from __future__ import annotations

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from uav_assistant.app.interfaces import (
    AlgorithmConfigurationRepository,
    AlgorithmSpecificConfiguration,
)
from uav_assistant.cross.enums import ObjectiveFunction
from uav_assistant.infra.db.postgre.models import (
    AlgorithmConfiguration as DbAlgorithmConfiguration,
)
from uav_assistant.infra.db.repos.codecs import (
    encode_configuration_parameters,
    get_configuration_codec,
)
from uav_assistant.infra.db.repos.convertors import AlgorithmConfigurationConvertor
from uav_assistant.infra.db.repos.utils import patch_update
from uav_assistant.infra.db.repos.validators import validate_id


class SqlAlchemyAlgorithmConfigurationRepository(AlgorithmConfigurationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, config_id: int) -> AlgorithmSpecificConfiguration:
        validate_id(config_id, "get", "AlgorithmConfiguration")
        result = await self._session.execute(
            select(DbAlgorithmConfiguration)
            .options(selectinload(DbAlgorithmConfiguration.mission))
            .where(DbAlgorithmConfiguration.id == config_id)
        )
        db_config = result.scalar_one_or_none()
        if db_config is None:
            raise ValueError(f"[get]: AlgorithmConfiguration with id {config_id} not found")

        config = AlgorithmConfigurationConvertor.to_domain(db_config)
        codec = get_configuration_codec(config.algo)
        return codec.decode(config, db_config.parameters)

    async def create(self, config: AlgorithmSpecificConfiguration) -> int:
        parent = config.config
        mission_id = parent.mission.id
        validate_id(mission_id, "create", "Mission")

        db_config = AlgorithmConfigurationConvertor.to_db(parent, mission_id)
        db_config.parameters = encode_configuration_parameters(config)

        self._session.add(db_config)
        await self._session.flush()
        return db_config.id

    async def update(
        self,
        config_id: int,
        config: AlgorithmSpecificConfiguration,
    ) -> None:
        validate_id(config_id, "update", "AlgorithmConfiguration")
        result = await self._session.execute(
            select(DbAlgorithmConfiguration).where(DbAlgorithmConfiguration.id == config_id)
        )
        db_config = result.scalar_one_or_none()
        if db_config is None:
            raise ValueError(f"[update]: AlgorithmConfiguration with id {config_id} not found")

        parent = config.config
        parameters = encode_configuration_parameters(config)
        values = patch_update(
            DbAlgorithmConfiguration.__mapper__.columns,
            {"id", "mission_id", "parameters"},
            db_config,
            parent,
        ) or {}

        if isinstance(values.get("objective"), ObjectiveFunction):
            values["objective"] = values["objective"].value
        if db_config.parameters != parameters:
            values["parameters"] = parameters
        if not values:
            return

        await self._session.execute(
            update(DbAlgorithmConfiguration)
            .where(DbAlgorithmConfiguration.id == config_id)
            .values(**values)
        )
        await self._session.flush()

    async def delete(self, config_id: int) -> None:
        validate_id(config_id, "delete", "AlgorithmConfiguration")
        await self._session.execute(
            delete(DbAlgorithmConfiguration).where(DbAlgorithmConfiguration.id == config_id)
        )
        await self._session.flush()
