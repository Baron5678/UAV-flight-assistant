from __future__ import annotations

import csv
import io
import zipfile
from typing import Iterable

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from uav_assistant.infra.db.postgre import get_session
from uav_assistant.infra.db.repos.mission import SqlAlchemyMissionRepository
from uav_assistant.infra.db.repos.mission_outcome import SqlAlchemyPathSummaryRepository
from uav_assistant.app.services.path_summary import PathSummaryService

router = APIRouter(tags=["export"])

def _write_final_paths_csv(
    buf: io.StringIO,
    rows: Iterable[tuple[int, str, str, int, float, float]],
) -> None:
    w = csv.writer(buf)
    w.writerow([
        "mission_id",
        "algo",
        "objective",
        "generation",
        "cost",
        "total_distance_m",
    ])
    for mission_id, algo, objective, gen, cost, dist_m in rows:
        w.writerow([mission_id, algo, objective, gen, cost, dist_m])


def _write_stats_csv(
    buf: io.StringIO,
    rows: Iterable[dict],
) -> None:
    w = csv.writer(buf)
    w.writerow([
        "mission_id",
        "algo",
        "objective",
        "generations",
        "population_size",
        "status",
        "best_cost",
        # stats
        "first_cost",
        "best_cost_run",
        "min_cost",
        "max_cost",
        "avg_cost",
        "improvement_abs",
        "improvement_pct",
        "improving_generations",
        "last_improvement_generation",
        "max_stagnation_generations",
        "min_total_distance_m",
        "max_total_distance_m",
        "avg_total_distance_m",
    ])
    for r in rows:
        w.writerow([
            r["mission_id"],
            r["algo"],
            r["objective"],
            r["generations"],
            r["population_size"],
            r["status"],
            r["mission_best_cost"],
            r["first_cost"],
            r["best_cost_run"],
            r["min_cost"],
            r["max_cost"],
            r["avg_cost"],
            r["improvement_abs"],
            r["improvement_pct"],
            r["improving_generations"],
            r["last_improvement_generation"],
            r["max_stagnation_generations"],
            r["min_total_distance_m"],
            r["max_total_distance_m"],
            r["avg_total_distance_m"],
        ])


def _write_path_evolve_csv(
    buf: io.StringIO,
    rows: Iterable[tuple[int, str, str, int, float, float]],
) -> None:
    w = csv.writer(buf)
    w.writerow([
        "mission_id",
        "algo",
        "objective",
        "generation",
        "cost",
        "total_distance_m",
    ])
    for mission_id, algo, objective, gen, cost, dist_m in rows:
        w.writerow([mission_id, algo, objective, gen, cost, dist_m])


@router.get("/export/all_csv.zip")
async def export_all_csv_zip(
    session: AsyncSession = Depends(get_session),
) -> StreamingResponse:

    mission_repo = SqlAlchemyMissionRepository(session)
    missions = await mission_repo.get_all()

    summary_repo = SqlAlchemyPathSummaryRepository(session)
    summary_svc = PathSummaryService(summary_repo)
    path_evolve_by_algo: dict[str, list[tuple[int, str, str, int, float, float]]] = {}
    final_by_algo: dict[str, list[tuple[int, str, str, int, float, float]]] = {}
    stats_by_algo: dict[str, list[dict]] = {}

    def algo_slug(algo: str) -> str:
        # normalize file prefix: "GA" -> "ga"
        return str(algo).strip().lower()

    for m in missions:
        mid = int(m.id)
        algo = str(getattr(m.algo, "value", m.algo))
        objective = str(getattr(m.objective, "value", m.objective))
        algo_key = algo_slug(algo)

        sums = await summary_svc.list_summaries(mid)

        # init buckets
        path_evolve_by_algo.setdefault(algo_key, [])
        final_by_algo.setdefault(algo_key, [])
        stats_by_algo.setdefault(algo_key, [])

        # evolve rows per algo
        for s in sums:
            path_evolve_by_algo[algo_key].append((
                mid,
                algo,
                objective,
                int(s.generation),
                float(s.cost),
                float(s.total_distance_m),
            ))

        # final row per algo
        if sums:
            final_s = max(sums, key=lambda x: int(x.generation))
            final_by_algo[algo_key].append((
                mid,
                algo,
                objective,
                int(final_s.generation),
                float(final_s.cost),
                float(final_s.total_distance_m),
            ))

        st = await summary_svc.compute_stats(mid)

        status = str(getattr(m.status, "value", m.status))
        mission_best_cost = float(getattr(m, "best_cost", 0.0) or 0.0)

        if st is None:
            stats_by_algo[algo_key].append({
                "mission_id": mid,
                "algo": algo,
                "objective": objective,
                "generations": int(getattr(m, "generations", 0) or 0),
                "population_size": int(getattr(m, "population_size", 0) or 0),
                "status": status,
                "mission_best_cost": mission_best_cost,
                "first_cost": "",
                "best_cost_run": "",
                "min_cost": "",
                "max_cost": "",
                "avg_cost": "",
                "improvement_abs": "",
                "improvement_pct": "",
                "improving_generations": "",
                "last_improvement_generation": "",
                "max_stagnation_generations": "",
                "min_total_distance_m": "",
                "max_total_distance_m": "",
                "avg_total_distance_m": "",
            })
        else:
            stats_by_algo[algo_key].append({
                "mission_id": mid,
                "algo": algo,
                "objective": objective,
                "generations": int(getattr(m, "generations", 0) or 0),
                "population_size": int(getattr(m, "population_size", 0) or 0),
                "status": status,
                "mission_best_cost": mission_best_cost,

                "first_cost": float(st.first_cost),
                "best_cost_run": float(st.best_cost),

                "min_cost": float(st.min_cost),
                "max_cost": float(st.max_cost),
                "avg_cost": float(st.avg_cost),

                "improvement_abs": float(st.improvement_abs),
                "improvement_pct": float(st.improvement_pct),

                "improving_generations": int(st.improving_generations),
                "last_improvement_generation": (
                    int(st.last_improvement_generation)
                    if st.last_improvement_generation is not None
                    else ""
                ),
                "max_stagnation_generations": int(st.max_stagnation_generations),

                "min_total_distance_m": float(st.min_total_distance_m),
                "max_total_distance_m": float(st.max_total_distance_m),
                "avg_total_distance_m": float(st.avg_total_distance_m),
            })

    zip_bytes = io.BytesIO()
    with zipfile.ZipFile(zip_bytes, mode="w", compression=zipfile.ZIP_DEFLATED) as z:

        # ✅ write 3 files per algo
        for algo_key in sorted(stats_by_algo.keys() | path_evolve_by_algo.keys() | final_by_algo.keys()):
            # stats
            stats_buf = io.StringIO()
            _write_stats_csv(stats_buf, stats_by_algo.get(algo_key, []))
            z.writestr(f"{algo_key}_stats.csv", stats_buf.getvalue().encode("utf-8"))

            # evolve
            evolve_buf = io.StringIO()
            _write_path_evolve_csv(evolve_buf, path_evolve_by_algo.get(algo_key, []))
            z.writestr(f"{algo_key}_path_evolve.csv", evolve_buf.getvalue().encode("utf-8"))

            # final
            final_buf = io.StringIO()
            _write_final_paths_csv(final_buf, final_by_algo.get(algo_key, []))
            z.writestr(f"{algo_key}_final_paths.csv", final_buf.getvalue().encode("utf-8"))

    zip_bytes.seek(0)

    return StreamingResponse(
        zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="uav_export.zip"'},
    )
