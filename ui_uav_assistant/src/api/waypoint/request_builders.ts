import type {
  AddWaypointRequestDto,
  DeleteWaypointRequestDto,
} from "./dto";

import type { WaypointRole } from "../../uav_types/waypoint";

export function buildAddWaypointRequest(args: {
  lat: number;
  lon: number;
  role: WaypointRole;
  name?: string;
}): AddWaypointRequestDto {
  return {
    lat: args.lat,
    lon: args.lon,
    role: args.role,
    name: args.name ?? "",
  };
}

export function buildDeleteWaypointRequest(waypointId: number): DeleteWaypointRequestDto {
  return { waypoint_id: waypointId };
}
