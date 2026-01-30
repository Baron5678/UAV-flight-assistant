import type { Algo, Objective } from "../../uav_types/algo";
import {PathRequestDto} from "./dto";

export function buildGeneratePathRequest(args: {
    missionId: number;
    generations: number;
    populationSize: number;
    seed: number
    mutationProbability: number
    keepElitism: number
    kTournament: number
    sigma0: number
    algo: Algo;
    objectiveFunction: Objective;
    batteryWh: number;
    whPerKm: number;
    reserveRatio?: number;
}): PathRequestDto {
    return {
        mission_id: args.missionId,
        generations: args.generations,
        population_size: args.populationSize,
        keep_elitism: args.keepElitism,
        seed: args.seed,
        k_tournament: args.kTournament,
        sigma0: args.sigma0,
        mutation_probability: args.mutationProbability,
        algo: args.algo,
        objective_function: args.objectiveFunction,
        drone: {
            battery_capacity_wh: args.batteryWh,
            wh_per_km: args.whPerKm,
            reserve_ratio: args.reserveRatio ?? 0.2,
        },
    };
}
