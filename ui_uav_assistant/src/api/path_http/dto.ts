import type {Algo, Objective} from "../../uav_types/algo";
import type { LatLonTuple } from "../../uav_types/path";

export interface DroneRequestDto {
    battery_capacity_wh: number;
    wh_per_km: number;
    reserve_ratio: number;
}

export interface PathRequestDto {
    mission_id: number;
    generations: number;
    population_size: number;
     seed?: number | null;
    mutation_probability?: number | null;
    keep_elitism?: number | null;
    k_tournament?: number | null;
    sigma0?: number | null;
    algo: Algo;
    objective_function: Objective;
    drone?: DroneRequestDto;
}

export interface PathResponseDto {
    type: "success"
    waypoint_ids: number[];
    waypoint_coords: LatLonTuple[];
    total_distance_m: number;
    best_cost: number;
    generations: number;
    population_size: number;
    seed: number;
    mutation_probability: number;
    keep_elitism: number;
    k_tournament: number;
    sigma0: number;
    algo: Algo;
}

export type PathPreviewHttpResponse = PathResponseDto | OptimizerErrorResponse;

export interface OptimizerErrorResponse {
  type: "diagnostic";
  feasible: false;
  message: string;
}