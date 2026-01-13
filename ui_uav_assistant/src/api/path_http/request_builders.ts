import type { Algo, Objective } from "../../uav_types/algo";
import {PathRequestDto} from "./dto";

export function buildGeneratePathRequest(args: {
  missionId: number;
  generations: number;
  populationSize: number;
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
    algo: args.algo,
    objective_function: args.objectiveFunction,
    drone: {
      battery_capacity_wh: args.batteryWh,
      wh_per_km: args.whPerKm,
      reserve_ratio: args.reserveRatio ?? 0.2,
    },
  };
}
