import { useMemo, useState } from "react";
import type { Waypoint } from "../uav_types/waypoint";
import type { MissionState, MissionStatus } from "../uav_types/mission";
import type { Path } from "../uav_types/path";
import type { TracerApi } from "../cross/logs";
import { startMissionHandler, finishMissionHandler, cancelMissionHandler } from "../handlers/mission";
import type { AlgoSettings } from "../uav_types/algo";

export interface UseMissionsResult {
  mission: MissionState;
  missionStatus: MissionStatus;
  resetMission: () => void;
  startMission: () => Promise<void>;
  finishMission: (path?: Path) => Promise<void>;
  cancelMission: () => Promise<void>;
}

export function useMissions(args: {
  waypoints: Waypoint[];
  tracer: TracerApi;
  settings: AlgoSettings;
}): UseMissionsResult {
  const [missionId, setMissionId] = useState<number | null>(null);
  const [missionStatus, setMissionStatus] = useState<MissionStatus>("idle");

  const mission = useMemo<MissionState>(
    () => ({
      id: missionId,
      setId: setMissionId,
      status: missionStatus,
      setStatus: setMissionStatus,
    }),
    [missionId, missionStatus]
  );

  const start = useMemo(
    () =>
      startMissionHandler({
        waypoints: args.waypoints,
        settings: args.settings,
        tracer: args.tracer,
        mission,
        clearPath: () => {},
      }),
    [args.waypoints, args.settings, args.tracer, mission]
  );

  const cancel = useMemo(
    () =>
      cancelMissionHandler({
        mission,
        tracer: args.tracer,
        clearPath: () => {},
      }),
    [mission, args.tracer]
  );

  function resetMission(): void {
    setMissionId(null);
    setMissionStatus("idle");
  }

  async function startMission(): Promise<void> {
    await start();
  }

  async function finishMission(path?: Path): Promise<void> {
    if (!path) {
      args.tracer.log("Generate a path before finishing mission.");
      return;
    }

    const finish = finishMissionHandler({
      mission,
      settings: args.settings,
      tracer: args.tracer,
      waypoint_ids: args.waypoints.map((w) => w.id),
      total_distance_m: path.total_distance_m,
      best_cost: path.cost,
    });

    await finish();
    setMissionStatus("idle");
  }

  async function cancelMission(): Promise<void> {
    await cancel();
    setMissionStatus("idle");
  }

  return {
    mission,
    missionStatus,
    resetMission,
    startMission,
    finishMission,
    cancelMission,
  };
}
