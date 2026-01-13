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
  algo: Algo;
}

export type PathPreviewHttpResponse = PathResponseDto | PostRunRouteValidationResponse;

export interface RouteEnergyFailureResponse {
  from_id: number;
  to_id: number;
  dist_m: number;
  soc_wh: number;
  reserve_wh: number;
  needed_wh: number;
  deficit_wh: number;
  deficit_m: number;
}

export interface PostRunRouteValidationResponse {
  type: "route_validation";
  feasible: false;
  objective: "ENERGY";
  failure: RouteEnergyFailureResponse;
}