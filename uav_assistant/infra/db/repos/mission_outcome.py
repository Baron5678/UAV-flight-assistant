from __future__ import annotations

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from uav_assistant.app.interfaces import MissionOutcomeRepository
from uav_assistant.domain.models import MissionOutcome as DomMissionOutcome
from uav_assistant.infra.db.postgre.models import MissionOutcome as DbMissionOutcome
from uav_assistant.infra.db.repos.convertors import MissionOutcomeConvertor, AlgorithmConfigurationConvertor
from uav_assistant.infra.db.postgre.models import AlgorithmConfiguration as DbAlgorithmConfig
from uav_assistant.infra.db.repos.utils import patch_update
from uav_assistant.infra.db.repos.validators import validate_id


class SqlAlchemyMissionOutcomeRepository(MissionOutcomeRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, config_id: int) -> DomMissionOutcome:
        validate_id(config_id, "get", "AlgorithmConfiguration")
        mission_outcome_res = await self._session.execute(
            select(DbMissionOutcome).
            where(DbMissionOutcome.config_id == config_id)
        )

        config_res = await self._session.execute(
            select(DbAlgorithmConfig)
            .options(selectinload(DbAlgorithmConfig.mission))
            .where(DbAlgorithmConfig.id == config_id)
        )

        mission_outcome = mission_outcome_res.scalar_one_or_none()
        if mission_outcome is None:
            raise ValueError(f"[get]: MissionOutcome with config_id {config_id} not found")
        config = config_res.scalar_one_or_none()
        if config is None:
            raise ValueError(f"[get]: AlgorithmConfiguration with id {config_id} not found")

        return MissionOutcomeConvertor.to_domain(
            mission_outcome,
            AlgorithmConfigurationConvertor.to_domain(config),
        )

    async def create(self, config_id: int, outcome: DomMissionOutcome) -> int:
        validate_id(config_id, "create", "AlgorithmConfiguration")
        db_outcome = MissionOutcomeConvertor.to_db(outcome, config_id)
        self._session.add(db_outcome)
        await self._session.flush()
        return db_outcome.id

    async def update(
            self,
            config_id: int,
            outcome: DomMissionOutcome,
    ) -> None:
        validate_id(config_id, "update", "AlgorithmConfiguration")

        result = await self._session.execute(
            select(DbMissionOutcome)
            .where(DbMissionOutcome.config_id == config_id)
        )

        db_outcome = result.scalar_one_or_none()

        if db_outcome is None:
            raise ValueError(
                f"[update]: MissionOutcome with config_id {config_id} not found"
            )

        excluded = {
            "id",
            "config_id",
            "mongo_result_id",
        }

        values = patch_update(DbMissionOutcome.__mapper__.columns, excluded, db_outcome, outcome)

        if values is None:
            return

        await self._session.execute(
            update(DbMissionOutcome)
            .where(DbMissionOutcome.config_id == config_id)
            .values(**values)
        )

        await self._session.flush()

    async def delete(self, config_id: int) -> None:
        validate_id(config_id, "delete", "AlgorithmConfiguration")
        await self._session.execute(
            delete(DbMissionOutcome).where(DbMissionOutcome.config_id == config_id)
        )
        await self._session.flush()


