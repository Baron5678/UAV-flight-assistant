# uav_assistant/transport/routers/http/path_summary.py

from __future__ import annotations

from typing import List, Optional, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from uav_assistant.infra.db.postgre import get_session
from uav_assistant.infra.db.repos.mission import SqlAlchemyMissionRepository
from uav_assistant.infra.db.repos.path_summary import SqlAlchemyPathSummaryRepository
from uav_assistant.app.services.path_summary import PathSummaryService, PathSummaryStats
from uav_assistant.transport.routers.http.models import PathSummaryResponse, PathSummaryRowResponse, \
    PathSummaryStatsResponse

router = APIRouter(tags=["summary"])


@router.get("/path_summary/{mission_id}", response_model=PathSummaryResponse)
async def path_summary(
    mission_id: int,
    session: AsyncSession = Depends(get_session),
) -> PathSummaryResponse:
    mission_repo = SqlAlchemyMissionRepository(session)
    mission = await mission_repo.get(mission_id)
    print(f"MISSION: {mission.id}")
    if mission is None:
        print("MISSION NOT FOUND")
        raise HTTPException(status_code=404, detail=f"Mission {mission_id} not found")

    repo = SqlAlchemyPathSummaryRepository(session)
    svc = PathSummaryService(repo)

    rows = await svc.list_summaries(mission_id)
    stats = await svc.compute_stats(mission_id)

    paths = [
        PathSummaryRowResponse(
            generation=int(r.generation),
            cost=float(r.cost),
            total_distance_m=float(r.total_distance_m),
        )
        for r in rows
    ]

    if stats is None:
        raise HTTPException(status_code=404, detail=f"Mission {mission_id} not found")


    stats_resp = PathSummaryStatsResponse(
        best_cost=float(stats.best_cost),
        first_cost=float(stats.first_cost),
        min_cost=float(stats.min_cost),
        max_cost=float(stats.max_cost),
        avg_cost=float(stats.avg_cost),
        min_total_distance_m=float(stats.min_total_distance_m),
        max_total_distance_m=float(stats.max_total_distance_m),
        avg_total_distance_m=float(stats.avg_total_distance_m),
        improvement_abs=float(stats.improvement_abs),
        improvement_pct=float(stats.improvement_pct),
        improving_generations=int(stats.improving_generations),
        last_improvement_generation=(
            int(stats.last_improvement_generation)
            if stats.last_improvement_generation is not None
            else None
        ),
        max_stagnation_generations=int(stats.max_stagnation_generations),
        )
    print(paths[0].cost, stats_resp.best_cost)

    return PathSummaryResponse(
        mission_id=int(mission_id),
        paths=paths,
        stats=stats_resp,
    )