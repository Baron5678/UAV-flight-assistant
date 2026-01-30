import { useMemo, useState } from "react";
import type { WaypointRole, Waypoint } from "../uav_types/waypoint";
import type { TracerApi } from "../cross/logs";
import { addWaypointHandler, deleteWaypointHandler } from "../handlers/waypoint";
import {make_request} from "../api/client/client";
import {AddWaypointResponseDto} from "../api/waypoint/dto";

export interface MapClickLatLng {
  lat: number;
  lng: number;
}

export interface UseWaypointResult {
    role: WaypointRole;
    setRole: (role: WaypointRole) => void;
    windSpeed: number
    setWindSpeed: (w: number) => void;
    windDirection: number
    setWindDirection: (w: number) => void;
    waypoints: Waypoint[];
    resetWaypoints: () => void;
    setAllWaypoints: (wps: Waypoint[]) => void;
    onMapClick: (latlng: MapClickLatLng) => Promise<void>;
    deleteWaypoint: (waypointId: number) => Promise<void>;
    addRandomWaypoints: (size: number, seed: number) => Promise<void>;
}

export function useWaypoints(tracer: TracerApi): UseWaypointResult {
  const [role, setRole] = useState<WaypointRole>("START");
  const [windSpeed, setWindSpeed] = useState<number>(0);
  const [windDirection, setWindDirection] = useState<number>(0);
  const [waypoints, setWaypoints] = useState<Waypoint[]>([]);

  const waypointState = useMemo(
    () => ({
        add: (wp: Waypoint) => setWaypoints((prev) => [...prev, wp]),
        addMany: (wps: Waypoint[]) => setWaypoints(wps),
        remove: (id: number) =>
            setWaypoints((prev) => prev.filter((w) => w.id !== id)),
    }),
    []
  );

  const setAllWaypoints = (wps: Waypoint[]) => setWaypoints(wps);

  const addWaypoint = useMemo(
    () => addWaypointHandler({ tracer, waypointState }),
    [tracer, waypointState]
  );

  const addRandomWaypoints = async (size: number, seed: number) => {
    const res = await make_request<AddWaypointResponseDto[], undefined>(
    "waypoint.add_random",
    undefined,
    undefined,
    { size, seed })
    if (res.failed) {
      tracer.log(`Add random waypoints failed (${res.http_status}): ${res.error}`);
      return;
    }
     setWaypoints((prev) => {
    const keep = prev.filter((w) => w.role === "START" || w.role === "END");
    const incoming = res.body.filter((w) => w.role !== "START" && w.role !== "END");
    return [...keep, ...incoming];
  });

    tracer.log(`Added ${res.body.length} random waypoints.`);
  };


  const deleteWaypoint = useMemo(
    () => deleteWaypointHandler({ tracer, waypointState }),
    [tracer, waypointState]
  );

  const onMapClick = async ({ lat, lng }: MapClickLatLng): Promise<void> => {
    await addWaypoint({ lat: lat, lon: lng, role: role, windSpeed: windSpeed, windDirection: windDirection, name: ""});
  };

  return {
      role,
      setRole,
      windSpeed,
      setWindSpeed,
      windDirection,
      setWindDirection,
      waypoints,
      setAllWaypoints: setAllWaypoints,
      resetWaypoints: () => setWaypoints([]),
      onMapClick,
      deleteWaypoint,
      addRandomWaypoints
  };
}
