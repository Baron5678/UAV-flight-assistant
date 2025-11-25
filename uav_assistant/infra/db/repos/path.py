from __future__ import annotations

from typing import Sequence, cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uav_assistant.domain.models import Path as DomPath
from uav_assistant.app.interfaces import PathRepository
from uav_assistant.infra.db.models import Path as DbPath, PathWaypoint as DbPathWaypoint


def to_domain(path_row: DbPath, waypoints_rows: Sequence[DbPathWaypoint]) -> DomPath:
    ordered = sorted(waypoints_rows, key=lambda pp: pp.seq)
    ids = [pp.waypoint_id for pp in ordered]
    return DomPath(
        waypoint_ids=ids,
        total_distance_m=path_row.distance_m,
        cost=path_row.cost,
    )

class SqlAlchemyPathRepository(PathRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(
        self,
        mission_id: int,
        path: DomPath,
        generation: int | None = None,
    ) -> DomPath:
        gen = generation if generation is not None else 0

        db_path = DbPath(
            mission_id=mission_id,
            generation=gen,
            cost=path.cost or 0.0,
            distance_m=path.total_distance_m or 0.0,
        )
        self.session.add(db_path)
        await self.session.flush()

        for seq, wp_id in enumerate(path.waypoint_ids, start=1):
            self.session.add(
                DbPathWaypoint(
                    path_id=db_path.id,
                    seq=seq,
                    waypoint_id=wp_id,
                )
            )

        return DomPath(
            waypoint_ids=list(path.waypoint_ids),
            total_distance_m=db_path.distance_m,
            cost=db_path.cost,
        )

    async def get_by_mission(self, mission_id: int) -> list[DomPath]:
        stmt = select(DbPath).where(DbPath.mission_id == mission_id)
        res = await self.session.execute(stmt)
        paths = res.scalars().all()

        result: list[DomPath] = []
        for p in paths:
            w_stmt = select(DbPathWaypoint).where(DbPathWaypoint.path_id == p.id)
            w_res = await self.session.execute(w_stmt)
            wp_rows = w_res.scalars().all()
            result.append(to_domain(p, wp_rows))
        return result

    async def get(self, path_id: int) -> DomPath:
        stmt = select(DbPath).where(DbPath.id == path_id)
        res = await self.session.execute(stmt)
        db_path = res.scalar_one_or_none()
        if db_path is None:
            raise ValueError(f"Path {path_id} not found")
        stmt = select(DbPathWaypoint).where(DbPathWaypoint.path_id == path_id)
        res = await self.session.execute(stmt)
        wp_rows = res.scalars().all()
        return to_domain(db_path, wp_rows)
