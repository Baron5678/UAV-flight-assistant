// // src/hooks/useMapData.jsx
// // @ts-nocheck
// import { useState, useCallback } from "react";
// import { apiAddWaypoint } from "../api/waypoints";
// import {
//   apiStartMission,
//   apiFinishMission,
//   apiCancelMission,
// } from "../api/mission";
//
// export function useMapData() {
//   // waypoint role selected in sidebar
//   const [role, setRole] = useState("START");
//   // all waypoints (WaypointResponse from backend)
//   const [waypoints, setWaypoints] = useState([]);
//
//   // mission state
//   const [missionId, setMissionId] = useState(null);
//   const [missionStatus, setMissionStatus] = useState("idle"); // "idle" | "active" | "finished"
//
//   // for later (path/finishMission)
//   const [lastPathPreview, setLastPathPreview] = useState(null);
//
//   // === POINTS: click on map -> add waypoint via backend ======================
//   const handleMapClick = useCallback(
//     async ({ lat, lng }) => {
//       try {
//         const created = await apiAddWaypoint({
//           lat,
//           lon: lng,
//           role,
//           name: "",
//         });
//
//         setWaypoints((prev) => [...prev, created]);
//       } catch (err) {
//         console.error(err);
//         alert("Failed to add waypoint: " + err.message);
//       }
//     },
//     [role]
//   );
//
//   // === MISSION: START ========================================================
//
//   const startMission = useCallback(async () => {
//     if (!waypoints.length) {
//       alert("Add waypoints first.");
//       return;
//     }
//
//     // START and END must exist – same idea as in old map.js
//     const startWp = waypoints.find(
//       (wp) => String(wp.role).toUpperCase() === "START"
//     );
//     const endWp = waypoints.find(
//       (wp) => String(wp.role).toUpperCase() === "END"
//     );
//
//     if (!startWp) {
//       alert("Please add a START waypoint.");
//       return;
//     }
//     if (!endWp) {
//       alert("Please add an END waypoint.");
//       return;
//     }
//
//     const waypointIds = waypoints.map((wp) => wp.id);
//
//     const generations = parseInt(
//       document.getElementById("gen")?.value ?? "0",
//       10
//     );
//     const populationSize = parseInt(
//       document.getElementById("pop")?.value ?? "0",
//       10
//     );
//     const algo = document.getElementById("algo")?.value || "GA";
//
//     try {
//       const data = await apiStartMission({
//         startWaypointId: startWp.id,
//         endWaypointId: endWp.id,
//         waypointIds,
//         generations: Number.isFinite(generations) ? generations : 0,
//         populationSize: Number.isFinite(populationSize) ? populationSize : 0,
//         algo,
//       });
//
//       // backend returns { mission_id, ... }
//       const mid = data.mission_id;
//       if (!mid) {
//         console.warn("startMission: backend response has no mission_id", data);
//       }
//
//       setMissionId(mid || null);
//       setMissionStatus("active");
//       setLastPathPreview(null);
//       // like map.js: disable Finish until we have a path
//       const finishBtn = document.getElementById("btn-finish");
//       if (finishBtn) finishBtn.disabled = true;
//     } catch (err) {
//       console.error(err);
//       alert("Failed to start mission: " + err.message);
//     }
//   }, [waypoints]);
//
//   // === MISSION: FINISH (will use lastPathPreview) ============================
//
//   const finishMission = useCallback(async () => {
//     if (!missionId) {
//       alert("No active mission.");
//       return;
//     }
//     if (!lastPathPreview) {
//       alert("Generate a path first.");
//       return;
//     }
//
//     const body = {
//       mission_id: missionId,
//       waypoint_ids: lastPathPreview.waypoint_ids,
//       total_distance_m: lastPathPreview.total_distance_m,
//       best_cost: lastPathPreview.best_cost,
//       generations: lastPathPreview.generations,
//       population_size: lastPathPreview.population_size,
//       algo: lastPathPreview.algo,
//     };
//
//     try {
//       const data = await apiFinishMission(body);
//       alert(
//         `Mission ${data.mission_id} finished. Saved path ID: ${data.path_id}`
//       );
//       setMissionStatus("finished");
//       const finishBtn = document.getElementById("btn-finish");
//       if (finishBtn) finishBtn.disabled = true;
//     } catch (err) {
//       console.error(err);
//       alert("Failed to finish mission: " + err.message);
//     }
//   }, [missionId, lastPathPreview]);
//
//   // === MISSION: CANCEL =======================================================
//
//   const cancelMission = useCallback(async () => {
//     if (!missionId) {
//       alert("No active mission.");
//       return;
//     }
//
//     try {
//       await apiCancelMission(missionId);
//       setMissionId(null);
//       setMissionStatus("idle");
//       setLastPathPreview(null);
//       // clear path layer in future when we have path state
//       const finishBtn = document.getElementById("btn-finish");
//       if (finishBtn) finishBtn.disabled = true;
//     } catch (err) {
//       console.error(err);
//       alert("Failed to cancel mission: " + err.message);
//     }
//   }, [missionId]);
//
//   // derived flags for buttons
//   const canStartMission = missionStatus === "idle" && waypoints.length > 0;
//   const canFinishMission = missionStatus === "active";
//   const canCancelMission = missionStatus === "active";
//
//   return {
//     // waypoints
//     role,
//     setRole,
//     waypoints,
//     setWaypoints,
//     handleMapClick,
//
//     // mission state
//     missionId,
//     missionStatus,
//     lastPathPreview,
//     setLastPathPreview, // will be used by path generation
//
//     // mission controls
//     canStartMission,
//     canFinishMission,
//     canCancelMission,
//     startMission,
//     finishMission,
//     cancelMission,
//   };
// }
