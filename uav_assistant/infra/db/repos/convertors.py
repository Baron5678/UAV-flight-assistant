from uav_assistant.cross.enums import Status, WaypointRole, ObjectiveFunction
from uav_assistant.domain.models import Mission as DomMission
from uav_assistant.infra.db.postgre.models import Mission as DbMission
from uav_assistant.domain.models import Waypoint as DomWaypoint
from uav_assistant.infra.db.postgre.models import Waypoint as DbWaypoint
from uav_assistant.domain.models import AlgorithmConfiguration as DomAlgorithmConfiguration
from uav_assistant.infra.db.postgre.models import AlgorithmConfiguration as DbAlgorithmConfiguration
from uav_assistant.domain.models import MissionOutcome as DomMissionOutcome
from uav_assistant.infra.db.postgre.models import MissionOutcome as DbMissionOutcome
from uav_assistant.domain.models import Drone as DomDrone
from uav_assistant.infra.db.postgre.models import Drone as DbDrone
from uav_assistant.domain.models import Path as DomPath
from uav_assistant.infra.db.mongo.models import PathSnapshotDocument


class MissionConvertor:
    @staticmethod
    def to_domain(db: DbMission) -> DomMission:
        return DomMission(
            id=db.id,
            name=db.name,
            status=Status(db.status),
        )

    @staticmethod
    def to_db(domain: DomMission) -> DbMission:
        return DbMission(
            id=domain.id,
            name=domain.name,
            status=domain.status.value,
        )

class WaypointConvertor:
    @staticmethod
    def to_domain(db: DbWaypoint) -> DomWaypoint:
        return DomWaypoint(
            id=db.id,
            name=db.name,
            lat=db.latitude,
            lon=db.longitude,
            role=WaypointRole(db.role),
            wind_speed=db.wind_speed,
            wind_direction=db.wind_direction,
            mission=MissionConvertor.to_domain(db.mission),
        )

    @staticmethod
    def to_db(domain: DomWaypoint, mission_id) -> DbWaypoint:
        return DbWaypoint(
            name=domain.name,
            latitude=domain.lat,
            longitude=domain.lon,
            role=domain.role.value,
            wind_speed=domain.wind_speed,
            wind_direction=domain.wind_direction,
            mission_id=mission_id
        )


class AlgorithmConfigurationConvertor:
    @staticmethod
    def to_domain(db: DbAlgorithmConfiguration) -> DomAlgorithmConfiguration:
        return DomAlgorithmConfiguration(
            mission=MissionConvertor.to_domain(db.mission),
            algo=db.algo,
            objective=ObjectiveFunction(db.objective),
            generations=db.generations,
            population_size=db.population_size,
            seed=db.seed,
        )

    @staticmethod
    def to_db(domain: DomAlgorithmConfiguration, mission_id) -> DbAlgorithmConfiguration:
        return DbAlgorithmConfiguration(
            mission_id=mission_id,
            algo=domain.algo,
            objective=str(domain.objective),
            generations=domain.generations,
            population_size=domain.population_size,
            seed=domain.seed,
        )

class MissionOutcomeConvertor:

    @staticmethod
    def to_domain(
        outcome: DbMissionOutcome,
        config: DomAlgorithmConfiguration,
    ) -> DomMissionOutcome:
        return DomMissionOutcome(
            config=config,
            first_cost=outcome.first_cost,
            best_cost=outcome.best_cost,
            min_cost=outcome.min_cost,
            max_cost=outcome.max_cost,
            avg_cost=outcome.avg_cost,
            improvement_abs=outcome.improvement_abs,
            improvement_pct=outcome.improvement_pct,
            improving_generations=outcome.improving_generations,
            last_improvement_generation=outcome.last_improvement_generation,
            max_stagnation_generations=outcome.max_stagnation_generations,
            min_total_distance_m=outcome.min_total_distance_m,
            max_total_distance_m=outcome.max_total_distance_m,
            avg_total_distance_m=outcome.avg_total_distance_m,
        )

    @staticmethod
    def to_db(
        outcome: DomMissionOutcome,
        config_id: int,
    ) -> DbMissionOutcome:
        return DbMissionOutcome(
            config_id=config_id,
            first_cost=outcome.first_cost,
            best_cost=outcome.best_cost,
            min_cost=outcome.min_cost,
            max_cost=outcome.max_cost,
            avg_cost=outcome.avg_cost,
            improvement_abs=outcome.improvement_abs,
            improvement_pct=outcome.improvement_pct,
            improving_generations=outcome.improving_generations,
            last_improvement_generation=outcome.last_improvement_generation,
            max_stagnation_generations=outcome.max_stagnation_generations,
            min_total_distance_m=outcome.min_total_distance_m,
            max_total_distance_m=outcome.max_total_distance_m,
            avg_total_distance_m=outcome.avg_total_distance_m,
        )

class PathSnapshotConvertor:
    @staticmethod
    def to_document(
        mission_id: int,
        config_id: int,
        domain: DomPath,
    ) -> PathSnapshotDocument:
        return {
            "mission_id": mission_id,
            "config_id": config_id,
            "generation": domain.generation,
            "waypoint_ids": domain.waypoint_ids,
            "cost": domain.cost,
            "distance_m": domain.distance_m,
        }

    @staticmethod
    def to_domain(document: PathSnapshotDocument) -> DomPath:
        return DomPath(
            waypoint_ids=list(document["waypoint_ids"]),
            generation=int(document["generation"]),
            distance_m=float(document["distance_m"]),
            cost=float(document["cost"]),
        )

class DroneConvertor:
    @staticmethod
    def to_domain(db: DbDrone) -> DomDrone:
        return DomDrone(
            name=db.name,
            speed=db.speed,
            battery_capacity_wh=db.battery_capacity_wh,
            per_meter_wh=db.per_meter_wh,
        )

    @staticmethod
    def to_db(domain: DomDrone) -> DbDrone:
        return DbDrone(
            name=domain.name,
            speed=domain.speed,
            battery_capacity_wh=domain.battery_capacity_wh,
            per_meter_wh=domain.per_meter_wh,
        )
