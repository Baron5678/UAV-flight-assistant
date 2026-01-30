import type {
    AddWaypointRequestDto,
    DeleteWaypointRequestDto,
} from "./dto";
import type { WaypointRole } from "../../uav_types/waypoint";
export function buildAddWaypointRequest(args: {
    lat: number;
    lon: number;
    role: WaypointRole;
    windSpeed: number;
    windDirection: number;
    name?: string;
}): AddWaypointRequestDto {
    return {
        lat: args.lat,
        lon: args.lon,
        role: args.role,
        wind_direction: args.windDirection,
        wind_speed: args.windDirection,
        name: args.name ?? "",
    };
}
export function buildDeleteWaypointRequest(waypointId: number): DeleteWaypointRequestDto {
    return { waypoint_id: waypointId };
}
