import * as React from "react";
import type { AddWaypointResponseDto } from "../api/waypoint/dto";
import type { WaypointRole } from "../uav_types/waypoint";
import { getRestore } from "../handlers/undo_waypoints";
type UseRestoreDeps = {
    setAllWaypoints: (wps: AddWaypointResponseDto[]) => void;
    clearPath?: () => void;
    clearTracer?: () => void;
    onTrace?: (line: string) => void;
};
export function useRestore(deps: UseRestoreDeps) {
    const { setAllWaypoints, clearPath, clearTracer, onTrace } = deps;
    return React.useCallback(
        async (missionId: number) => {
            clearPath?.();
            clearTracer?.();

            const resp = await getRestore(missionId);

            const restored: AddWaypointResponseDto[] = resp.waypoints.map((w) => ({
                id: w.id,
                lat: w.lat,
                lng: w.lng,
                role: w.role as WaypointRole,
                wind_speed: w.wind_speed,
                wind_direction: w.wind_direction,
                name: w.name ?? "",
            }));

            setAllWaypoints(restored);
            onTrace?.(`Restored ${restored.length} waypoints from path_id=${resp.path_id}.`);
            },
        [setAllWaypoints, clearPath, clearTracer, onTrace]
    );
}
