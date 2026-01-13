import {Algo, Objective} from "../../uav_types/algo";
export interface StartMissionRequestDto {
  name?: string;
  start_waypoint_id: number;
  end_waypoint_id: number;
  waypoint_ids: number[];
  generations: number;
  population_size: number;
  objective: Objective;
  algo: Algo;
}

export interface StartMissionResponseDto {
  mission_id: number;
}

export interface FinishMissionRequestDto {
    mission_id: number
    waypoint_ids: number[]
    total_distance_m: number
    best_cost: number
    generations: number
    population_size: number
    algo: Algo
}

export interface FinishMissionResponseDto {
  mission_id: number;
  path_id?: number;
  cost?: number;
}

export interface CancelMissionRequestDto {
  mission_id: number;
}

export interface CancelMissionResponseDto {
  mission_id: number;
}
