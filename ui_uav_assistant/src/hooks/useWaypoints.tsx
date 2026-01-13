import { useMemo, useState } from "react";
import type { WaypointRole, Waypoint } from "../uav_types/waypoint";
import type { TracerApi } from "../cross/logs";
import { addWaypointHandler, deleteWaypointHandler } from "../handlers/waypoint";

export interface MapClickLatLng {
  lat: number;
  lng: number;
}

export interface UseWaypointResult {
    role: WaypointRole;
    setRole: (role: WaypointRole) => void;
    waypoints: Waypoint[];
    resetWaypoints: () => void;
    onMapClick: (latlng: MapClickLatLng) => Promise<void>;
    deleteWaypoint: (waypointId: number) => Promise<void>;
}

export function useWaypoints(tracer: TracerApi): UseWaypointResult {
  const [role, setRole] = useState<WaypointRole>("START");
  const [waypoints, setWaypoints] = useState<Waypoint[]>([]);

  const waypointState = useMemo(
    () => ({
      add: (wp: Waypoint) => setWaypoints((prev) => [...prev, wp]),
      remove: (id: number) =>
          setWaypoints((prev) => prev.filter((w) => w.id !== id)),
    }),
    []
  );

  const addWaypoint = useMemo(
    () => addWaypointHandler({ tracer, waypointState }),
    [tracer, waypointState]
  );

  const deleteWaypoint = useMemo(
    () => deleteWaypointHandler({ tracer, waypointState }),
    [tracer, waypointState]
  );

  const onMapClick = async ({ lat, lng }: MapClickLatLng): Promise<void> => {
    await addWaypoint({ lat: lat, lon: lng, role: role, name: ""});
  };

  return {
    role,
    setRole,
    waypoints,
    resetWaypoints: () => setWaypoints([]),
    onMapClick,
    deleteWaypoint,
  };
}
