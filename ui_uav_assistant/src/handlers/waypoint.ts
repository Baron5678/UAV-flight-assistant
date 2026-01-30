import type { TracerApi } from "../cross/logs";
import { buildAddWaypointRequest, buildDeleteWaypointRequest } from "../api/waypoint/request_builders";
import { make_request, ResponseUAV } from "../api/client/client";
import { AddWaypointResponseDto, DeleteWaypointResponseDto } from "../api/waypoint/dto";
import { Waypoint, WaypointRole, WaypointState } from "../uav_types/waypoint";
export function addWaypointHandler(args: {
    tracer: TracerApi;
    waypointState: WaypointState;
}) {
    return async function handleAddWaypoint(input: {
        lat: number;
        lon: number;
        role: WaypointRole;
        windSpeed: number;
        windDirection: number;
        name?: string;
    }): Promise<void> {
        const dto = buildAddWaypointRequest(input);
        const res: ResponseUAV<AddWaypointResponseDto> = await make_request("waypoint.add", dto);
        if (res.failed) {
            args.tracer.log(res.error);
            return;
        }
        const wp: Waypoint = {
            id: res.body.id,
            role: res.body.role,
            lat: res.body.lat,
            lng: res.body.lng,
            wind_direction: res.body.wind_direction,
            wind_speed: res.body.wind_speed
        };
        args.waypointState.add(wp);
        args.tracer.log(`Waypoint added: ${wp.id}`);
    };
}
export function deleteWaypointHandler(args: {
    tracer: TracerApi;
    waypointState: WaypointState;
}) {
    return async function handleDeleteWaypoint(waypointId: number): Promise<void> {
        const dto = buildDeleteWaypointRequest(waypointId);
        const res: ResponseUAV<DeleteWaypointResponseDto> = await make_request("waypoint.delete", dto);
        if (res.failed) {
            args.tracer.log(res.error);
            return;
        }
        args.waypointState.remove(waypointId);
        args.tracer.log(`Waypoint deleted: ${waypointId}`);
    };
}
