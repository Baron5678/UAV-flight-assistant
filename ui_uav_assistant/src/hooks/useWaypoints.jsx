// @ts-nocheck
import { useState, useCallback, useEffect } from "react";
import {apiAddWaypoint, apiDeleteWaypoint} from "../api/waypoints";

export function useWaypoints() {
  const [role, setRole] = useState("START");

  const [waypoints, setWaypoints] = useState([]);

  const handleMapClick = useCallback(
    async ({ lat, lng }) => {
      try {
        const created = await apiAddWaypoint({
          lat,
          lon: lng,
          role,
          name: "",
        });
        setWaypoints((prev) => [...prev, created]);
      } catch (err) {
        console.error(err);
        alert("Failed to add waypoint: " + err.message);
      }
    },
    [role]
  );

  const resetWaypoints = useCallback(() => {
    setWaypoints([]);
  }, []);

    const deleteWaypoint = useCallback(async (id) => {
    try {
      await apiDeleteWaypoint(id);
      setWaypoints((prev) => prev.filter((wp) => wp.id !== id));
    } catch (err) {
      console.error(err);
      alert("Failed to delete waypoint: " + err.message);
    }
  }, []);

  return {
    role,
    setRole,
    waypoints,
    setWaypoints,
    handleMapClick,
      resetWaypoints,
      deleteWaypoint
  };
}
