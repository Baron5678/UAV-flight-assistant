import type { PathResponseDto } from "../path_http/dto";
import type { LatLonTuple } from "../../uav_types/path";

export type PathProgressEvent =
  | PathGenerationEvent
  | PathFinalEvent
  | PathErrorEvent;

export interface PathGenerationEvent {
  type: "generation";
  generation: number;
  cost: number;
  waypoint_coords: LatLonTuple[];
}

export interface PathFinalEvent {
  type: "final";
  cost: number
  payload: PathResponseDto;
}

export interface PathErrorEvent {
  type: "error";
  error: string;
}
