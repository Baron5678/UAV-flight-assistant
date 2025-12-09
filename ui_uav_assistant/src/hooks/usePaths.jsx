// src/hooks/usePaths.jsx
// @ts-nocheck
import { useState, useCallback } from "react";
import { apiGeneratePath } from "../api/paths";
import { startPathProgress } from "../api/pathProgressWS";  // ADD this


/**
 * Manages path preview for a given mission:
 * - pathCoords: [[lat, lng], ...]
 * - pathCost: number
 * - lastPathPreview: full PathResponse from backend
 */
export function usePaths(missionId) {
  const [pathCoords, setPathCoords] = useState(null);
  const [pathCost, setPathCost] = useState(null);
  const [lastPathPreview, setLastPathPreview] = useState(null);

  const generatePathPreview = useCallback(async () => {
    if (!missionId) {
      alert("Start a mission first.");
      return;
    }

    const generations = parseInt(
      document.getElementById("gen")?.value ?? "0",
      10
    );
    const populationSize = parseInt(
      document.getElementById("pop")?.value ?? "0",
      10
    );
    const algo = document.getElementById("algo")?.value || "GA";

    const battery = parseFloat(
      document.getElementById("energy")?.value ?? "0"
    );
    const ratio = parseFloat(
      document.getElementById("ratio")?.value ?? "0"
    );

    try {
      const data = await apiGeneratePath({
        missionId,
        generations: Number.isFinite(generations) ? generations : 0,
        populationSize: Number.isFinite(populationSize) ? populationSize : 0,
        algo,
        batteryWh: Number.isFinite(battery) ? battery : 0,
        whPerKm: Number.isFinite(ratio) ? ratio : 0,
      });

      // store full PathResponse
      setLastPathPreview(data);

      // coords for drawing polyline
      const coords = (data.waypoint_coords || []).map(([lat, lon]) => [
        lat,
        lon,
      ]);
      setPathCoords(coords);
      setPathCost(data.best_cost ?? data.cost ?? null);

      // update "Best Cost" input
      if (typeof data.best_cost === "number") {
        const costInput = document.getElementById("cost");
        if (costInput) costInput.value = data.best_cost.toFixed(2);
      }
    } catch (err) {
      console.error(err);
      alert("Failed to generate path: " + err.message);
    }
  }, [missionId]);

  const clearPath = useCallback(() => {
    setLastPathPreview(null);
    setPathCoords(null);
    setPathCost(null);
    const costInput = document.getElementById("cost");
    if (costInput) costInput.value = "";
  }, []);

  const hasPath = !!lastPathPreview;

  return {
    pathCoords,
    pathCost,
    lastPathPreview,
    hasPath,
    generatePathPreview,
    clearPath,
  };
}

export function usePathsWS(missionId) {
  const [pathCoords, setPathCoords] = useState(null);
  const [pathCost, setPathCost] = useState(null);
  const [lastPathPreview, setLastPathPreview] = useState(null);
    const [lastPathRequest, setLastPathRequest] = useState(null);

  // id of active websocket, if you want to store/close it later
  const [wsRef, setWsRef] = useState(null);

  const clearPath = useCallback(() => {
    setPathCoords(null);
    setPathCost(null);
    setLastPathPreview(null);

    const costInput = document.getElementById("cost");
    if (costInput) costInput.value = "";
  }, []);

  /**
   * requestBody: same content as POST /path (PathRequest)
   * options.onTrace: optional callback to write log lines into Tracer
   */
  const generatePathPreview = useCallback(
    (requestBody, options = {}) => {
      const { onTrace } = options;

      if (!missionId) {
        const msg = "Cannot generate path: mission has not been started.";
        console.warn(msg);
        onTrace && onTrace(msg);
        return;
      }

          setLastPathRequest(requestBody);   // <- store PathRequest


      // start WebSocket streaming
      const ws = startPathProgress({
        requestBody,
        onGeneration: (msg) => {
          // update path every generation
          if (Array.isArray(msg.waypoint_coords)) {
            setPathCoords(msg.waypoint_coords);
          }
          if (typeof msg.best_cost === "number") {
            setPathCost(msg.best_cost);
            const costInput = document.getElementById("cost");
            if (costInput) costInput.value = msg.best_cost.toFixed(2);
          }
          if (onTrace && msg.message) {
            onTrace(msg.message);
          }
        },
        onFinal: (msg) => {
          // final route + cost
          if (Array.isArray(msg.waypoint_coords)) {
            setPathCoords(msg.waypoint_coords);
          }
          if (typeof msg.best_cost === "number") {
            setPathCost(msg.best_cost);
            const costInput = document.getElementById("cost");
            if (costInput) costInput.value = msg.best_cost.toFixed(2);
          }
          // treat final WS message as "PathResponse-like"
          setLastPathPreview(msg);

          if (onTrace && msg.message) {
            onTrace(msg.message);
          }
        },
        onError: (err) => {
          const errMsg = `WebSocket error while generating path: ${
            err?.message || "Unknown error"
          }`;
          console.error(errMsg);
          onTrace && onTrace(errMsg);
        },
      });

      setWsRef(ws);
    },
    [missionId]
  );

  const hasPath = !!lastPathPreview;

  return {
    pathCoords,
    pathCost,
    lastPathPreview,
      lastPathRequest,   // <- expose PathRequest
    hasPath,
    generatePathPreview, // now WS-based
    clearPath,
  };
}