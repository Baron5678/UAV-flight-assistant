import type {
    StartMissionRequestDto,
    FinishMissionRequestDto,
    CancelMissionRequestDto,
} from "./dto";
import type {Algo, Objective} from "../../uav_types/algo";
export function buildStartMissionRequest(args: {
    name?: string;
    startWaypointId: number;
    endWaypointId: number;
    waypointIds: number[];
    generations: number;
    populationSize: number;
    seed: number
    mutation_probability: number
    keep_elitism: number
    k_tournament: number
    sigma0: number
    objectiveFunction: Objective;
    algo: Algo;
}): StartMissionRequestDto {
    return {
        name: args.name ?? "default_mission",
        start_waypoint_id: args.startWaypointId,
        end_waypoint_id: args.endWaypointId,
        waypoint_ids: args.waypointIds,
        generations: args.generations,
        population_size: args.populationSize,
        objective: args.objectiveFunction,
        k_tournament: args.k_tournament,
        keep_elitism: args.keep_elitism,
        seed: args.seed,
        sigma0: args.sigma0,
        mutation_probability: args.mutation_probability,
        algo: args.algo,
    };
}
export function buildFinishMissionRequest(args: {
    missionId: number;
    waypointIds: number[];
    totalDistanceM: number;
    bestCost: number;
    generations: number;
    populationSize: number;
    seed: number
    mutation_probability: number
    keep_elitism: number
    k_tournament: number
    sigma0: number
    algo: "GA" | "ES";
}): FinishMissionRequestDto {
    return {
        mission_id: args.missionId,    waypoint_ids: args.waypointIds,
        total_distance_m: args.totalDistanceM,
        best_cost: args.bestCost,
        generations: args.generations,
        population_size: args.populationSize,
        k_tournament: args.k_tournament,
        keep_elitism: args.keep_elitism,
        seed: args.seed,
        sigma0: args.sigma0,
        mutation_probability: args.mutation_probability,
        algo: args.algo,
    };
}
export function buildCancelMissionRequest(missionId: number): CancelMissionRequestDto {
    return { mission_id: missionId };
}
