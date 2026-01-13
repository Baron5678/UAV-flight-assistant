# uav_assistant/infra/db/repos/path_summary.py

from __future__ import annotations

from typing import Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from uav_assistant.app.interfaces import PathSummaryRepository
from uav_assistant.domain.models import PathSummary as DomPathSummary
from uav_assistant.infra.db.models import PathSummary as DbPathSummary


class SqlAlchemyPathSummaryRepository(PathSummaryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, summary: DomPathSummary) -> None:
        row = DbPathSummary(
            mission_id=int(summary.mission_id),
            generation=int(summary.generation),
            cost=float(summary.cost),
            total_distance_m=float(summary.total_distance_m),
        )
        self._session.add(row)
        await self._session.flush()

    async def add_many(self, summaries: Sequence[DomPathSummary]) -> None:
        if not summaries:
            return
        rows = [
            DbPathSummary(
                mission_id=int(s.mission_id),
                generation=int(s.generation),
                cost=float(s.cost),
                total_distance_m=float(s.total_distance_m),
            )
            for s in summaries
        ]
        self._session.add_all(rows)
        await self._session.flush()

    async def list_by_mission(self, mission_id: int) -> list[DomPathSummary]:
        stmt = (
            select(DbPathSummary)
            .where(DbPathSummary.mission_id == int(mission_id))
            .order_by(DbPathSummary.generation.asc())
        )
        res = await self._session.execute(stmt)
        rows = res.scalars().all()
        return [
            DomPathSummary(
                mission_id=int(r.mission_id),
                generation=int(r.generation),
                cost=float(r.cost),
                total_distance_m=float(r.total_distance_m),
            )
            for r in rows
        ]

    async def delete_for_mission(self, mission_id: int) -> None:
        await self._session.execute(
            delete(DbPathSummary).where(DbPathSummary.mission_id == int(mission_id))
        )
        await self._session.flush()
