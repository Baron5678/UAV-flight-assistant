// src/hooks/useMission.jsx
// @ts-nocheck
import { useState, useCallback } from "react";
import {
  apiStartMission,
  apiFinishMission,
  apiCancelMission,
} from "../api/mission";

/**
 * Mission lifecycle only.
 * - depends on waypoints for startMission()
 * - finishMission(pathPreview) consumes path data from usePaths
 */
export function useMission(waypoints) {
  const [missionId, setMissionId] = useState(null);
  const [missionStatus, setMissionStatus] = useState("idle"); // idle | active | finished

  // ---- START ---------------------------------------------------------------
  const startMission = useCallback(async () => {
    if (!waypoints || !waypoints.length) {
      alert("Add waypoints first.");
      return;
    }

    const normRole = (wp) => String(wp.role || "").toUpperCase();

    const startWp = waypoints.find((wp) => normRole(wp) === "START");
    const endWp = waypoints.find((wp) => normRole(wp) === "END");

    if (!startWp) {
      alert("Please add a START waypoint.");
      return;
    }
    if (!endWp) {
      alert("Please add an END waypoint.");
      return;
    }

    const waypointIds = waypoints.map((wp) => wp.id);

    const generations = parseInt(
      document.getElementById("gen")?.value ?? "0",
      10
    );
    const populationSize = parseInt(
      document.getElementById("pop")?.value ?? "0",
      10
    );
    const algo = document.getElementById("algo")?.value || "GA";

    try {
      const data = await apiStartMission({
        startWaypointId: startWp.id,
        endWaypointId: endWp.id,
        waypointIds,
        generations: Number.isFinite(generations) ? generations : 0,
        populationSize: Number.isFinite(populationSize) ? populationSize : 0,
        algo,
      });

      const mid = data.mission_id;
      setMissionId(mid || null);
      setMissionStatus("active");
    } catch (err) {
      console.error(err);
      alert("Failed to start mission: " + err.message);
    }
  }, [waypoints]);

  // ---- FINISH: consumes pathPreview from usePaths --------------------------
  const finishMission = useCallback(
    async (pathPreview, pathRequest) => {
      if (!missionId) {
        alert("No active mission.");
        return;
      }
      if (!pathPreview) {
        alert("Generate a path first.");
        return;
      }

      const body = {
      mission_id: missionId,
      waypoint_ids: pathPreview.waypoint_ids,
      total_distance_m: pathPreview.total_distance_m,
      best_cost: pathPreview.best_cost,
      generations:
        pathPreview.generations ?? pathRequest.generations,
      population_size:
        pathPreview.population_size ?? pathRequest.population_size,
      algo: pathPreview.algo ?? pathRequest.algo,
    };

      try {
        const data = await apiFinishMission(body);
        alert(
          `Mission ${data.mission_id} finished. Saved path ID: ${data.path_id}`
        );
        setMissionStatus("complete");
      } catch (err) {
        console.error(err);
        alert("Failed to finish mission: " + err.message);
      }
    },
    [missionId]
  );

  // ---- CANCEL --------------------------------------------------------------
  const cancelMission = useCallback(async () => {
    if (!missionId) {
      alert("No active mission.");
      return;
    }

    try {
      await apiCancelMission(missionId);
      setMissionId(null);
      setMissionStatus("idle");
    } catch (err) {
      console.error(err);
      alert("Failed to cancel mission: " + err.message);
    }
  }, [missionId]);

  const resetMission = useCallback(() => {
    setMissionId(null);
    setMissionStatus("idle");
  }, []);

  return {
    missionId,
    missionStatus,
      setMissionStatus,
    startMission,
    finishMission,
    cancelMission,
      resetMission
  };
}
