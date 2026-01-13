import { useCallback, useMemo, useState } from "react";

import { apiResetAll } from "../api/reset/resetAll";
import { useTracer } from "./useTracer";

import { useWaypoints } from "./useWaypoints";
import { useMissions } from "./useMissions";
import { usePathsWS } from "./usePathWs";
import { usePathsHttp } from "./usePathHttp";

import type { Drone } from "../uav_types/drone";
import type { AlgoSettings } from "../uav_types/algo";
import { buildGeneratePathRequest } from "../api/path_http/request_builders";
import type { PathRenderMode } from "../uav_types/path";
import type { MapClickLatLng } from "./useWaypoints";

export function useUavAppController() {
  // Tracer
  const { lines: tracerLines, log, clear: clearTracer, tracer } = useTracer();

  // Typed settings (React-form state)
  const [drone, setDrone] = useState<Drone>(
    () =>
      ({
        batteryWh: 100,
        whPerKm: 10,
        reserveRatio: 0.2,
      }) as Drone
  );

  const [algoSettings, setAlgoSettings] = useState<AlgoSettings>(
    () =>
      ({
        algo: "GA",
        generations: 30,
        populationSize: 20,
        objectiveFunction: "DISTANCE",
      }) as AlgoSettings
  );

  const [streamGenerations, setStreamGenerations] = useState<boolean>(false);

  const {
    role,
    setRole,
    waypoints,
    resetWaypoints,
    onMapClick,
    deleteWaypoint,
  } = useWaypoints(tracer);

  const { mission, missionStatus, startMission, finishMission, cancelMission, resetMission } =
    useMissions({
      waypoints,
      tracer,
      settings: algoSettings,
    });

  const pathsWS = usePathsWS({
    mission,
    tracer,
    onTrace: log,
  });

  const pathsHttp = usePathsHttp({
    mission,
    tracer,
    algoSettings,
    drone,
  });

  const activePath = streamGenerations ? pathsWS.path : pathsHttp.path;
  const activePathCoords = streamGenerations
    ? pathsWS.pathCoords
    : activePath?.waypoint_coords ?? null;
  const activePathCost = streamGenerations
    ? pathsWS.pathCost
    : (activePath?.cost ?? null);

  const activeHasPath = streamGenerations ? pathsWS.hasPath : pathsHttp.hasPath;
  const onDeleteWaypointSafe = useCallback(
    async (id: number) => {
      if (missionStatus === "active") {
        alert("Cancel mission before deleting waypoints.");
        return;
      }
      await deleteWaypoint(id);
    },
    [missionStatus, deleteWaypoint]
  );

  const onStartMissionSafe = useCallback(async () => {
    pathsWS.cancel();
    pathsWS.clearPath();
    pathsHttp.clearPath();
    clearTracer();
    await startMission();
  }, [pathsWS, pathsHttp, clearTracer, startMission]);

  const onCancelMissionSafe = useCallback(async () => {
    pathsWS.cancel();
    pathsWS.clearPath();
    pathsHttp.clearPath();
    clearTracer();
    await cancelMission();
  }, [pathsWS, pathsHttp, clearTracer, cancelMission]);

  const onGeneratePathSafe = useCallback(async () => {
    if (!mission.id) {
      alert("Start a mission first.");
      return;
    }

    if (streamGenerations) {
      pathsHttp.clearPath();

     const req = buildGeneratePathRequest({
    missionId: mission.id,
    generations: algoSettings.generations,
     populationSize: algoSettings.populationSize,
     algo: algoSettings.algo,
    objectiveFunction: algoSettings.objectiveFunction, // add this
    batteryWh: drone.batteryWh,
    whPerKm: drone.whPerKm,
    reserveRatio: drone.reserveRatio,
    });


      const mode: PathRenderMode = "EACH_GENERATION";

      log(
        `Mission ${mission.id}: starting ${req.algo} path computation (${req.generations} generations, pop=${req.population_size})…`
      );

      pathsWS.start(req, mode);
      return;
    }

    pathsWS.cancel();
    pathsWS.clearPath();

    log(`Mission ${mission.id}: generating path (HTTP)…`);
    try {
      await pathsHttp.generatePathHttp();
    } catch (err: any) {
      console.error(err);
      log(`Path generation failed: ${err?.message ?? String(err)}`);
    }
  }, [
    mission.id,
    streamGenerations,
    algoSettings,
    drone,
    clearTracer,
    log,
    pathsWS,
    pathsHttp,
  ]);


  const onFinishMissionSafe = useCallback(async () => {
    if (!activePath) {
      alert("Generate scouting path before finishing mission.");
      return;
    }
    await finishMission(activePath);
    clearTracer();
    pathsWS.clearPath();
    pathsHttp.clearPath();
  }, [activePath, finishMission, clearTracer, pathsWS.clearPath, pathsHttp]);

  const onResetApplicationSafe = useCallback(async () => {
    try {
      await apiResetAll();
    } catch (err: any) {
      console.error(err);
      alert("Failed to reset backend: " + (err?.message ?? String(err)));
    }

    pathsWS.cancel();
    pathsWS.clearPath();
    pathsHttp.clearPath();
    resetWaypoints();
    resetMission();
    clearTracer();
  }, [pathsWS, pathsHttp, resetWaypoints, resetMission, clearTracer]);

  const onMapClickSafe = useMemo(() => onMapClick, [onMapClick]);

  return {
      role,
      setRole,
      drone,
      setDrone,
      algoSettings,
      setAlgoSettings,
      streamGenerations,
      setStreamGenerations,
      tracerLines,
      missionStatus,
      missionId: mission.id,
      waypoints,
      pathCoords: activePathCoords,
      pathCost: activePathCost,
      hasPath: activeHasPath,
      onMapClick: onMapClickSafe as (p: MapClickLatLng) => Promise<void>,
      onDeleteWaypoint: onDeleteWaypointSafe,
      onStartMission: onStartMissionSafe,
      onFinishMission: onFinishMissionSafe,
      onGeneratePath: onGeneratePathSafe,
      onCancelMission: onCancelMissionSafe,
      onResetApplication: onResetApplicationSafe,
  };
}
