from __future__ import annotations
from typing import Any, Mapping, Sequence
import numpy as np

from uav_assistant.domain.metrics import distance_m
from uav_assistant.domain.models import Waypoint, AlgoSettings, PreRunReport, UnreachableRequired


def _role_name(wp: Any) -> str:
    role_obj = getattr(wp, "role", None)
    return str(getattr(role_obj, "value", role_obj)).upper()


def pre_run_energy(
    *,
    points: Sequence[Waypoint],
    end_id: int | None,
    settings: AlgoSettings,
    allow_finish_without_station: bool = True,
) -> PreRunReport:
    id2wp: Mapping[int, Waypoint] = {int(p.id): p for p in points}

    required_ids: list[int] = []
    station_ids: list[int] = []

    for p in points:
        rn = _role_name(p)
        if rn == "REQUIRED":
            required_ids.append(int(p.id))
        elif rn == "STATION":
            station_ids.append(int(p.id))

    battery_wh = float(settings.battery_wh)
    per_meter_wh = float(settings.per_meter_wh)
    reserve_ratio = float(settings.reserve_ratio)

    reserve_wh = battery_wh * reserve_ratio
    usable_wh = battery_wh - reserve_wh
    max_leg_m = float(usable_wh / per_meter_wh) if per_meter_wh > 0 else float("inf")
    targets: list[int] = list(station_ids)
    if allow_finish_without_station and end_id is not None:
        targets.append(int(end_id))

    problems: list[UnreachableRequired] = []

    for rid in required_ids:
        wp_r = id2wp.get(rid)
        if wp_r is None:
            problems.append(
                UnreachableRequired(
                    required_id=rid,
                    nearest_station_id=-1,
                    dist_required_to_station_m=float("inf"),
                    max_leg_m=max_leg_m,
                    nearest_required_id=None,
                    dist_required_to_required_m=None,
                )
            )
            continue

        best_station_dist = float("inf")
        best_station_id: int | None = None
        for tid in targets:
            wp_t = id2wp.get(int(tid))
            if wp_t is None:
                continue
            d = float(distance_m(wp_r.position, wp_t.position))
            if np.isfinite(d) and d < best_station_dist:
                best_station_dist = d
                best_station_id = int(tid)

        best_req_dist = float("inf")
        best_req_id: int | None = None
        for rid2 in required_ids:
            if rid2 == rid:
                continue
            wp_r2 = id2wp.get(rid2)
            if wp_r2 is None:
                continue
            d2 = float(distance_m(wp_r.position, wp_r2.position))
            if np.isfinite(d2) and d2 < best_req_dist:
                best_req_dist = d2
                best_req_id = rid2

        if best_station_id is None or (not np.isfinite(best_station_dist)):
            problems.append(
                UnreachableRequired(
                    required_id=rid,
                    nearest_station_id=-1,
                    dist_required_to_station_m=float("inf"),
                    max_leg_m=max_leg_m,
                    nearest_required_id=best_req_id,
                    dist_required_to_required_m=(best_req_dist if np.isfinite(best_req_dist) else None),
                )
            )
            continue

        if best_station_dist > max_leg_m:
            problems.append(
                UnreachableRequired(
                    required_id=rid,
                    nearest_station_id=best_station_id,
                    dist_required_to_station_m=best_station_dist,
                    max_leg_m=max_leg_m,
                    nearest_required_id=best_req_id,
                    dist_required_to_required_m=(best_req_dist if np.isfinite(best_req_dist) else None),
                )
            )

    return PreRunReport(
        feasible=(len(problems) == 0),
        max_leg_m=max_leg_m,
        problems=problems,
    )

