from typing import Sequence
from uav_assistant.app.interfaces import PathOptimizer
from uav_assistant.domain.models import Mission, Waypoint, Drone, Path
from uav_assistant.domain.metrics import distance_h, build_distance_matrix, distance_m
from uav_assistant.infra.es.es import run_es
from uav_assistant.infra.ga.genetic_algorithm import run_ga


class GAPathOptimizer(PathOptimizer):
    async def optimize(
        self,
        mission: Mission,
        drones: Sequence[Drone],
        candidates: Sequence[Waypoint],
    ) -> Path:
        ids = {w.id for w in list(candidates)}
        if mission.start_waypoint_id not in ids or mission.end_waypoint_id not in ids:
            raise ValueError("Start or end waypoint not in candidates")
        graph = build_distance_matrix(list(candidates))
        best_route_ids, best_cost = run_ga(
            points=list(candidates),
            graph=graph,
            start_id=mission.start_waypoint_id,
            end_id=mission.end_waypoint_id,
            generations=mission.generations,
            pop_size=mission.population_size,
        )
        id_to_wp = {w.id: w for w in candidates}
        total_dist = 0.0
        for a, b in zip(best_route_ids, best_route_ids[1:]):
            wp_a = id_to_wp[a]
            wp_b = id_to_wp[b]
            total_dist += distance_m(wp_a.position, wp_b.position)

        return Path(
            waypoint_ids=best_route_ids,
            total_distance_m=total_dist,
            cost=best_cost,
        )

class ESPathOptimizer(PathOptimizer):
    async def optimize(
        self,
        mission: Mission,
        drones: Sequence[Drone],
        candidates: Sequence[Waypoint],
    ) -> Path:
        ids = {w.id for w in candidates}
        if mission.start_waypoint_id not in ids or mission.end_waypoint_id not in ids:
            raise ValueError("Start or end waypoint not in candidates")

        best_route_ids, best_cost = run_es(
            points=list(candidates),
            start_id=mission.start_waypoint_id,
            end_id=mission.end_waypoint_id,
            generations=mission.generations,
            pop_size=mission.population_size,
        )

        id_to_wp = {w.id: w for w in candidates}

        total_dist = 0.0
        for a, b in zip(best_route_ids, best_route_ids[1:]):
            wp_a = id_to_wp[a]
            wp_b = id_to_wp[b]
            total_dist += distance_m(wp_a.position, wp_b.position)

        return Path(
            waypoint_ids=best_route_ids,
            total_distance_m=total_dist,
            cost=best_cost,
        )
