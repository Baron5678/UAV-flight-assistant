from typing import Sequence, Mapping

import numpy as np

from uav_assistant.domain.metrics import distance_m
from uav_assistant.domain.models import Waypoint, PostRunReport, RouteEnergyFailure


def post_run_energy(
    route_ids: Sequence[int],
    id2wp: Mapping[int, Waypoint],
    *,
    battery_wh: float,
    per_meter_wh: float,
    reserve_ratio: float,
) -> PostRunReport:
    if not route_ids or len(route_ids) < 2:
        return PostRunReport(feasible=False, total_dist_m=0.0, station_visits=0,
                             failure=None)

    soc = float(battery_wh)
    reserve = float(battery_wh * reserve_ratio)
    total_dist = 0.0
    station_visits = 0

    prev_id = route_ids[0]
    for cur_id in route_ids[1:]:
        wp_prev = id2wp[prev_id]
        wp_cur = id2wp[cur_id]

        dist = float(distance_m(wp_prev.position, wp_cur.position))
        print(f"Distance: {dist}")
        total_dist += dist
        prev_id = cur_id
        if not np.isfinite(dist) or dist < 0:
            return PostRunReport(
                feasible=False,
                total_dist_m=float("inf"),
                station_visits=station_visits,
                failure=RouteEnergyFailure(prev_id, cur_id, float("inf"), soc, reserve, float("inf")),
            )

        total_dist += dist

        needed = dist * per_meter_wh
        if not np.isfinite(needed) or needed < 0:
            return PostRunReport(
                feasible=False,
                total_dist_m=float("inf"),
                station_visits=station_visits,
                failure=RouteEnergyFailure(prev_id, cur_id, dist, soc, reserve, float("inf")),
            )

        if soc - needed < reserve:
            print(f"Reserve: {needed}")
            return PostRunReport(
                feasible=False,
                total_dist_m=total_dist,
                station_visits=station_visits,
                failure=RouteEnergyFailure(prev_id, cur_id, dist, soc, reserve, needed),
            )

        soc -= needed

        role_obj = getattr(wp_cur, "role", None)
        role_name = str(getattr(role_obj, "value", role_obj)).upper()
        if role_name == "STATION":
            soc = float(battery_wh)
            station_visits += 1

        prev_id = cur_id

    return PostRunReport(feasible=True, total_dist_m=total_dist, station_visits=station_visits, failure=None)
